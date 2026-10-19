using System;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Relics;
using KleeMod.Tests.Harness;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Models;
using Xunit;

namespace KleeMod.Tests.Prototype;

/// <summary>
/// SEAT PAGE BACKLOG BURN (2026-10-19), the mod's half. Things that happened
/// with nothing on the page saying so: four Kokomi relics, orb passives and
/// evokes, and an amplifier's factor. Each now files a page event or names
/// its factor; structural pins and pure words (the headless boundary). The
/// page half is <c>tier0/tests/test_seat_page_backlog_2026_10_19.py</c>.
/// </summary>
[Collection(KleeOverhaulArm.Name)]
public class SeatPageBacklog20261019Tests : IDisposable
{
    public SeatPageBacklog20261019Tests()
    {
        FurinaStageLedger.ResetAll();
    }

    public void Dispose()
    {
        FurinaStageLedger.ResetAll();
    }

    private static string[] Calls(string type, string method) =>
        Il.Calls(Il.Method(type, method)).ToArray();

    // ---- the two event kinds ------------------------------------------------

    [Fact]
    public void The_two_page_event_kinds_are_spelled_once()
    {
        Assert.Equal("relic", ResolutionLedger.RelicDid);
        Assert.Equal("orb", ResolutionLedger.OrbFired);
        Assert.Equal("passive", ResolutionLedger.OrbPassive);
        Assert.Equal("evoked", ResolutionLedger.OrbEvoked);
        Assert.Contains("ResolutionLedger.NoteEvent",
                        Calls("ResolutionLedger", "NoteRelic"));
        Assert.Contains("ResolutionLedger.NoteEvent",
                        Calls("ResolutionLedger", "NoteOrb"));
    }

    // ---- the Kokomi relics --------------------------------------------------

    [Fact]
    public void The_casket_names_its_block()
    {
        Assert.Contains("ResolutionLedger.NoteRelic",
                        Calls("TamakushiCasket", "AfterCardPlayed"));
        Assert.Equal("gained 1 Block", TamakushiCasket.BlockNote(1));
        Assert.Equal("Tamakushi Casket", new TamakushiCasket().RelicName);
        Assert.Equal("Watatsumi Casket", new WatatsumiCasket().RelicName);
    }

    [Fact]
    public void Sango_pearl_says_its_discount_is_spent()
    {
        Assert.Contains("ResolutionLedger.NoteRelic",
                        Calls("SangoPearl", "AfterCardPlayed"));
        Assert.Equal("refunded 2 Energy, used this combat",
                     SangoPearl.SpentNote(2));
        Assert.Equal("used this combat", SangoPearl.SpentNote(0));
    }

    [Fact]
    public void Moonglow_says_where_the_card_went()
    {
        Assert.Contains("ResolutionLedger.NoteRelic",
                        Calls("EverlastingMoonglow", "Return"));
        Assert.Equal("returned Ward to your hand",
                     EverlastingMoonglow.ReturnNote("Ward", handFull: false));
        Assert.Equal("your hand was full, so Ward went to your Discard Pile",
                     EverlastingMoonglow.ReturnNote("Ward", handFull: true));
    }

    [Fact]
    public void The_clam_says_what_its_mend_healed()
    {
        Assert.Contains("ResolutionLedger.NoteRelic",
                        Calls("OceanHuedClam", "Mend"));
        Assert.Equal("Mend 1, healed 1 HP", OceanHuedClam.MendNote(1, 1));
        Assert.Equal("Mend 1, healed 0 HP (Mend stops at your HP when the "
                     + "fight began)", OceanHuedClam.MendNote(1, 0));
    }

    // ---- orbs ---------------------------------------------------------------

    private static HarmonyMethod Target(string patch) =>
        typeof(OrbNarration).Assembly.GetType("KleeMod.Powers." + patch)!
            .GetCustomAttribute<HarmonyPatch>()!.info;

    [Fact]
    public void Each_orb_door_is_patched_by_name_and_parameter()
    {
        var passive = Target("OrbModel_TriggerPassive_Narration_Patch");
        Assert.Equal(typeof(OrbModel), passive.declaringType);
        Assert.Equal(nameof(OrbModel.TriggerPassive), passive.methodName);

        var direct = Target("OrbCmd_Passive_Narration_Patch");
        Assert.Equal(typeof(OrbCmd), direct.declaringType);
        var passiveCmd = AccessTools.Method(typeof(OrbCmd), direct.methodName)!;
        Assert.Contains(passiveCmd.GetParameters(),
                        p => p.Name == "orb" && p.ParameterType == typeof(OrbModel));
        Assert.Contains(passiveCmd.GetParameters(),
                        p => p.Name == "countAffectedByHooks");

        // The evoke door is private: Harmony binds it by name, so the name
        // and the parameter the prefix reads must both still be there.
        var evoke = Target("OrbCmd_Evoke_Narration_Patch");
        Assert.Equal(typeof(OrbCmd), evoke.declaringType);
        var evokeCmd = AccessTools.Method(typeof(OrbCmd), evoke.methodName)!;
        Assert.Contains(evokeCmd.GetParameters(),
                        p => p.Name == "evokedOrb" && p.ParameterType == typeof(OrbModel));
    }

    // ---- the amplifier's factor ---------------------------------------------

    [Fact]
    public void An_amplified_hit_and_its_reaction_row_name_the_factor()
    {
        Assert.Equal("Pyro, Vaporize 1.5x",
            ResolutionLedger.ElementLabel(Element.Pyro, Reaction.Vaporize, 1.5m));
        Assert.Equal("Cryo, Melt 2x",
            ResolutionLedger.ElementLabel(Element.Cryo, Reaction.Melt, 2m));
        Assert.Equal("1.75x", ResolutionLedger.Factor(1.75m));
        Assert.Equal("The hit that set it off dealt 1.5x damage.",
                     ResolutionLedger.AmplifiedDetail(1.5m));
        Assert.Contains("ReactionLog.DetailNextIfNone",
                        Calls("ReactionEffects", "Resolve"));
    }

    // ---- Claque's Ledger ----------------------------------------------------

    [Fact]
    public void Claques_ledger_files_its_own_gain_beat()
    {
        var mods = new StageMods { ClaquesLedger = 1 };
        var kit = StageKit.With(mods, 0, StagePerformer.Wriothesley);
        StageKit.Run(kit.Director.ActAll());
        var gain = Assert.Single(kit.Stage.Beats,
            b => b.Event == FurinaStageLedger.GainEvent
                 && b.Source == StageDirector.ClaquesLedgerTitle);
        Assert.Equal(1, gain.Moved);
        // A beat no performer made names nobody on the wire (it carried
        // the enum's default, Charlotte, onto the page).
        Assert.True(FurinaStageLedger.NoPerformer(gain));
        Assert.False(FurinaStageLedger.NoPerformer(kit.Stage.Beats[0]));
    }
}
