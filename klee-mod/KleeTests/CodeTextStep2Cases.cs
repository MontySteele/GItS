using System;
using System.Collections.Generic;
using KleeMod.Cards;
using KleeMod.Elements;
using KleeMod.Powers;
using KleeMod.Tests.Prototype;
using KleeMod.Vfx;

namespace KleeMod.Tests;

/// <summary>
/// CODE-BUILT TEXT, KEYED, STEP 2 (Varka and Furina; the localization census,
/// 2026-10-23). The cases the parity proof renders: every pure surface step 2
/// keyed, over the inputs that reach each of its branches. Their English
/// before the keying was dumped off the old assembly (main 2b5f235b1) into
/// <c>Fixtures/code_text_before_2026_10_23.json</c> under <c>s2:</c>; the
/// reaction preview's three amplified bodies, private to their method then,
/// were dumped from that method's own interpolations.
/// </summary>
internal static class CodeTextStep2Cases
{
    internal static readonly Element[] OathElements =
        { Element.Pyro, Element.Hydro, Element.Cryo, Element.Electro };

    internal static IEnumerable<(string Key, Func<string> Render)> All(
        Func<Element, decimal, int, int, string> setOffFirst,
        Func<decimal, int, Element, int, string> foldedHere,
        Func<decimal, Element, int, int, string> foldedElsewhere,
        Func<string, bool, string> withBoot)
    {
        // ---- Varka: the face lines -------------------------------------------
        foreach (var e in OathElements)
        {
            foreach (var oath in new[] { 0, 1, 3 })
            {
                yield return ($"s2:varka:switch:{e}:{oath}", () => VarkaOath.SwitchWords(e, oath));
            }
            foreach (var times in new[] { 0, 1, 2, 3 })
            {
                yield return ($"s2:varka:pays:{e}:{times}", () => VarkaOath.SwirlPays(e, times));
                yield return ($"s2:varka:swirlline:{e}:{times}",
                              () => VarkaOath.SwirlWords(true, VarkaOath.SwirlPays(e, times)));
            }
        }
        yield return ("s2:varka:pays:None:1", () => VarkaOath.SwirlPays(Element.None, 1));
        yield return ("s2:varka:swirl:False", () => VarkaOath.SwirlWords(false));
        yield return ("s2:varka:swirl:True", () => VarkaOath.SwirlWords(true));
        yield return ("s2:varka:swirl:False:pays",
                      () => VarkaOath.SwirlWords(false, VarkaOath.SwirlPays(Element.Hydro, 1)));
        yield return ("s2:varka:swirl:True:empty", () => VarkaOath.SwirlWords(true, ""));
        yield return ("s2:varka:noaura", () => VarkaOath.NoAuraToSwirl);
        foreach (var damage in new[] { 0, 1, 5 })
        {
            yield return ($"s2:varka:wildfire:{damage}", () => VarkaOath.WildfireWords(damage));
        }

        // ---- Varka: the Oath gains said over his head ---------------------------
        foreach (var e in OathElements)
        {
            foreach (var n in new[] { 1, 2 })
            {
                foreach (var source in new[] { OathSource.Other, OathSource.Applied, OathSource.Swirl })
                {
                    yield return ($"s2:varka:gain:{e}:{n}:{source}", () => VarkaOath.GainClause(e, n, source));
                }
            }
        }
        var one = new[] { VarkaOath.GainClause(Element.Pyro, 1, OathSource.Applied) };
        var three = new[]
        {
            VarkaOath.GainClause(Element.Pyro, 1, OathSource.Applied),
            VarkaOath.GainClause(Element.Hydro, 1, OathSource.Swirl),
            VarkaOath.GainClause(Element.Cryo, 2, OathSource.Other),
        };
        yield return ("s2:varka:gainline:none", () => VarkaOath.GainLine("Amber: Precise Shot", Array.Empty<string>(), null));
        yield return ("s2:varka:gainline:one", () => VarkaOath.GainLine(null, one, null));
        yield return ("s2:varka:gainline:one:card", () => VarkaOath.GainLine("Amber: Precise Shot", one, null));
        yield return ("s2:varka:gainline:three:card", () => VarkaOath.GainLine("Amber: Precise Shot", three, null));
        yield return ("s2:varka:gainline:three:fang", () => VarkaOath.GainLine("Kaeya: Frostgnaw", three, "Boreas's Fang"));
        yield return ("s2:varka:gainline:one:nocard:fang", () => VarkaOath.GainLine("", one, "Wolf's Gravestone"));

        // ---- Sucrose's clause and "below half" ----------------------------------
        yield return ("s2:swirlaura:True", () => SwirlAuraFace.Words(true));
        yield return ("s2:swirlaura:False", () => SwirlAuraFace.Words(false));
        yield return ("s2:swirlaura:const", () => SwirlAuraFace.NoAura);
        foreach (var max in new[] { 1, 78, 79, 100 })
        {
            yield return ($"s2:halfhp:{max}", () => HalfHpFace.Words(max));
        }

        // ---- Furina: the face lines ----------------------------------------------
        var full = StageKit.Of(StagePerformer.Wriothesley, StagePerformer.Lynette, StagePerformer.Clorinde);
        foreach (var who in Enum.GetValues<StagePerformer>())
        {
            yield return ($"s2:bow:full:{who}", () => FurinaStageBowPreview.Line(full.Stage, who));
            yield return ($"s2:bow:repeat:{who}", () => FurinaStageBowPreview.Line(StageKit.Of(who).Stage, who));
            var evict = StageKit.Of(who, who == StagePerformer.Navia ? StagePerformer.Lyney : StagePerformer.Navia,
                                    who == StagePerformer.Neuvillette ? StagePerformer.Lyney : StagePerformer.Neuvillette);
            yield return ($"s2:bow:evict:{who}",
                          () => FurinaStageBowPreview.Line(evict.Stage, who == StagePerformer.Escoffier
                              ? StagePerformer.Charlotte : StagePerformer.Escoffier));
        }
        yield return ("s2:bow:empty", () => FurinaStageBowPreview.Line(StageKit.Of().Stage, StagePerformer.Charlotte));
        foreach (var (returns, past) in new[] { (0, 0), (4, 0), (0, 3), (4, 2), (1, 1) })
        {
            foreach (var pastReturns in new[] { false, true })
            {
                yield return ($"s2:drain:tag:{returns}:{past}:{pastReturns}",
                              () => FurinaStageFacePreview.DrainTag(returns, past, pastReturns));
            }
        }
        yield return ("s2:drain:split", () => FurinaStageFacePreview.SplitTag(4, 2));
        yield return ("s2:drain:returns", () => FurinaStageFacePreview.ReturnsTag);
        yield return ("s2:drain:pastlost", () => FurinaStageFacePreview.PastLineLost);
        yield return ("s2:drain:pastreturns", () => FurinaStageFacePreview.PastLineReturns);
        yield return ("s2:drain:notenough", () => FurinaStageFacePreview.NotEnoughHp);
        foreach (var (amount, masquerade, freminet) in new[]
                 { (3, 0, false), (3, 1, false), (3, 2, true), (2, 0, true), (0, 1, true) })
        {
            yield return ($"s2:drain:block:{amount}:{masquerade}:{freminet}",
                          () => FurinaStageFacePreview.DrainBlock(amount, masquerade, freminet));
        }
        foreach (var lost in new[] { -1, 0, 7 })
        {
            yield return ($"s2:lost:{lost}", () => FurinaStageFacePreview.LostThisCombatWords(lost));
        }
        yield return ("s2:spend:short", () => FurinaStageFacePreview.NotEnoughFanfare);
        foreach (var spend in new[] { 0, 2, 4, 6, 8, 13 })
        {
            foreach (var all in new[] { false, true })
            {
                yield return ($"s2:spend:hits:{spend}:{all}", () => FurinaStageFacePreview.SpendUpToHitsWords(spend, all));
            }
        }
        foreach (var repays in new[] { 0, 1, 3 })
        {
            yield return ($"s2:repay:{repays}", () => FurinaStageFacePreview.Line(repays));
            foreach (var payout in new[] { "", FurinaStageFacePreview.PayBlock, FurinaStageFacePreview.PayVigor,
                                           FurinaStageFacePreview.PayDamage })
            {
                foreach (var perHp in new[] { 1, 2 })
                {
                    yield return ($"s2:repay:{repays}:3:{payout}:{perHp}",
                                  () => FurinaStageFacePreview.Line(repays, 3, payout, perHp));
                }
            }
        }

        // ---- Furina: the Drained counter and the Fanfare gauge --------------------
        foreach (var lineZero in new[] { false, true })
        {
            foreach (var pastReturns in new[] { false, true })
            {
                yield return ($"s2:drained:buffer:{lineZero}:{pastReturns}",
                              () => DrainedCounter.BufferSentence(7, lineZero, pastReturns));
            }
        }
        foreach (var (drained, past) in new[] { (0, 0), (12, 0), (12, 4) })
        {
            foreach (var pastReturns in new[] { false, true })
            {
                yield return ($"s2:drained:phrase:{drained}:{past}:{pastReturns}",
                              () => DrainedCounter.DrainedPhrase(drained, past, pastReturns));
            }
        }
        foreach (var returning in new[] { -1, 0, 9 })
        {
            yield return ($"s2:drained:returns:{returning}", () => DrainedCounter.ReturnsLine(returning));
        }
        foreach (var (guests, regina) in new[] { (0, 0), (3, 0), (0, 4), (3, 4) })
        {
            yield return ($"s2:drained:coming:{guests}:{regina}", () => DrainedCounter.ComingLines(guests, regina));
        }
        yield return ("s2:drained:hover:empty", () => DrainedCounter.HoverBody(0, 0));
        yield return ("s2:drained:hover:full",
                      () => DrainedCounter.HoverBody(12, 5, false, 4, false, 7, 3, 2));
        yield return ("s2:drained:hover:zero",
                      () => DrainedCounter.HoverBody(10, 0, true, 0, true, 10, 0, 6));
        yield return ("s2:fanfare:hover:0:0", () => FanfareCounter.HoverBody(0, 0));
        yield return ("s2:fanfare:hover:3:5", () => FanfareCounter.HoverBody(3, 5));

        // ---- Furina: the stage cue's forecast line --------------------------------
        yield return ("s2:cue:repay", () => FurinaStageCues.ForecastLine(
            new StageForecastCue(StagePerformer.Charlotte, 0, StageCueKind.Repay, 3, "", "")));
        yield return ("s2:cue:block", () => FurinaStageCues.ForecastLine(
            new StageForecastCue(StagePerformer.Freminet, 0, StageCueKind.Block, 4, "", "")));
        yield return ("s2:cue:aura", () => FurinaStageCues.ForecastLine(
            new StageForecastCue(StagePerformer.Lynette, 0, StageCueKind.Damage, 5, "Anemo", StageForecastCue.Aura)));
        yield return ("s2:cue:all", () => FurinaStageCues.ForecastLine(
            new StageForecastCue(StagePerformer.Escoffier, 0, StageCueKind.Damage, 4, "Cryo", StageForecastCue.All)));
        yield return ("s2:cue:random", () => FurinaStageCues.ForecastLine(
            new StageForecastCue(StagePerformer.Clorinde, 0, StageCueKind.Damage, 6, "Electro", StageForecastCue.Random)));

        // ---- The card-hover reaction riders ---------------------------------------
        foreach (var e in ElementWords.All)
        {
            yield return ($"s2:tip:override:{e}", () => KleeCardTooltips.OverriddenElementBody(e));
        }
        foreach (var boss in new[] { false, true })
        {
            yield return ($"s2:tip:frozenartifact:{boss}", () => KleeCardTooltips.FrozenArtifactBody(boss));
            yield return ($"s2:tip:frozenartifact:{boss}:named",
                          () => KleeCardTooltips.FrozenArtifactBody(boss, "Cryo Slime"));
        }
        foreach (var (reaction, debuff) in new[] { (Reaction.Overload, "Weak"),
                                                   (Reaction.Superconduct, "Vulnerable"),
                                                   (Reaction.ElectroCharged, "Poison") })
        {
            yield return ($"s2:tip:debuffartifact:{reaction}", () => KleeCardTooltips.DebuffArtifactSentence(debuff));
            yield return ($"s2:tip:debuffartifact:{reaction}:named",
                          () => KleeCardTooltips.DebuffArtifactSentence(debuff, "Cryo Slime"));
        }
        yield return ("s2:tip:spendonly", () => KleeCardTooltips.SpendOnly("BODY"));
        foreach (var reaction in new[] { Reaction.Vaporize, Reaction.Melt })
        {
            yield return ($"s2:tip:nohit:{reaction}", () => KleeCardTooltips.NoHitBody(reaction)!);
        }
        foreach (var aura in OathElements)
        {
            foreach (var others in new[] { false, true })
            {
                yield return ($"s2:tip:swirl:{aura}:{others}",
                              () => KleeCardTooltips.SwirlPreviewBody(aura, others, 3, Element.None, ""));
            }
            yield return ($"s2:tip:swirl:{aura}:oath",
                          () => KleeCardTooltips.SwirlPreviewBody(aura, true, 5, aura, ""));
            yield return ($"s2:tip:swirl:{aura}:oath:pays",
                          () => KleeCardTooltips.SwirlPreviewBody(aura, false, 3, aura, VarkaOath.SwirlPays(Element.Hydro, 2)));
            yield return ($"s2:tip:swirl:{aura}:pays",
                          () => KleeCardTooltips.SwirlPreviewBody(aura, true, 3, Element.None, VarkaOath.SwirlPays(Element.Pyro, 1)));
        }
        foreach (var (mult, aura) in new[] { (1.5m, Element.Hydro), (1.75m, Element.Cryo), (2.00m, Element.Pyro),
                                             (1.875m, Element.Hydro) })
        {
            foreach (var boot in new[] { false, true })
            {
                yield return ($"s2:tip:amp:setoff:{mult}:{aura}:{boot}",
                              () => withBoot(setOffFirst(aura, mult, 7, 9), boot));
                yield return ($"s2:tip:amp:here:{mult}:{aura}:{boot}",
                              () => withBoot(foldedHere(mult, 18, aura, 18), boot));
                yield return ($"s2:tip:amp:elsewhere:{mult}:{aura}:{boot}",
                              () => withBoot(foldedElsewhere(mult, aura, 14, 21), boot));
            }
        }
    }
}
