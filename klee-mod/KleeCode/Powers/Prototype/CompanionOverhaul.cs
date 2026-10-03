namespace KleeMod.Powers;

/// <summary>
/// The numbers the overhaul's POWERS carry. Every one is lifted verbatim off
/// the workshop's own printed text (its sec.3, re-priced in its sec.8) --
/// nothing here is derived and nothing is picked. They are named constants
/// rather than literals at the call sites because the sim is LAW and the
/// mirrors must be comparable BY VALUE (<c>tools/lint_constant_parity.py</c>).
///
/// A number a CARD prints stays on the card row, where the codegen renders it
/// into a DynamicVar; only a number a POWER carries lands here.
/// </summary>
public static class CompanionOverhaulLaw
{
    /// <summary>Diona, Signature Mix: Block at the start of each of 2 turns.
    /// Mirrors <c>C.MC_SIGNATURE_MIX_BLOCK</c>.</summary>
    public const int SignatureMixBlock = 4;

    /// <summary>Kaeya, Glacial Waltz: Cryo damage per end of turn, 3 turns.
    /// Mirrors <c>C.MC_GLACIAL_WALTZ_DMG</c>.</summary>
    public const int GlacialWaltzDamage = 6;

    /// <summary>Albedo, Solar Isotoma: the platform's own damage.
    /// Mirrors <c>C.MC_ISOTOMA_DMG</c>.</summary>
    public const int IsotomaDamage = 8;

    /// <summary>Albedo, Solar Isotoma: the Crystallize half.
    /// Mirrors <c>C.MC_ISOTOMA_BLOCK</c>.</summary>
    public const int IsotomaBlock = 4;

    /// <summary>Jean, Dandelion Breeze: Block per end of turn.
    /// Mirrors <c>C.MC_DANDELION_BREEZE_BLOCK</c>.</summary>
    public const int DandelionBreezeBlock = 6;

    /// <summary>Fischl, Oz at Your Side: the Electro volley, no turn limit.
    /// Mirrors <c>C.MC_OZ_DMG</c>.</summary>
    public const int OzDamage = 5;

    /// <summary>Nicole, Revelation: Block at the start of your turn.
    /// Mirrors <c>C.MC_REVELATION_BLOCK</c>.</summary>
    public const int RevelationBlock = 5;

    /// <summary>Nicole, Revelation: Theosis, for holding the line.
    /// Mirrors <c>C.MC_REVELATION_STRENGTH</c>.</summary>
    public const int RevelationStrength = 2;

    /// <summary>Mona, Stellaris Phantasm: the delayed doom, one turn of it.
    /// Mirrors <c>C.MC_OMEN_VULNERABLE</c>.</summary>
    public const int OmenVulnerable = 1;

    /// <summary>Lisa, Lightning Rose: Electro damage per end of turn.
    /// Mirrors <c>C.MC_LIGHTNING_ROSE_DMG</c>.</summary>
    public const int LightningRoseDamage = 5;

    /// <summary>Lisa, Lightning Rose: the Vulnerable that rides it.
    /// Mirrors <c>C.MC_LIGHTNING_ROSE_VULN</c>.</summary>
    public const int LightningRoseVulnerable = 1;

    // THE SECOND WAVE -- the thirteen rows whose printed text needed an engine
    // hook. Same rule as the eleven above: a number the CARD prints stays on
    // the card row and is rendered into a DynamicVar, and only a number a
    // POWER carries lands here.

    /// <summary>Dahlia, Sacramental Shower: what the trap answers with.
    /// Mirrors <c>C.MC_SHOWER_DMG</c>.</summary>
    public const int ShowerDamage = 9;

    /// <summary>Razor, Lightning Fang: damage his Attacks gain, 2 turns.
    /// Mirrors <c>C.MC_LIGHTNING_FANG_BONUS</c>.</summary>
    public const int LightningFangDamage = 3;

    /// <summary>Amber, Baron Bunny: the Pyro the decoy answers with.
    /// Mirrors <c>C.MC_BARON_BUNNY_DMG</c>.</summary>
    public const int BaronBunnyDamage = 8;

    /// <summary>Eula, Lightfall Sword: the blade's own damage.
    /// Mirrors <c>C.MC_LIGHTFALL_BASE</c>.</summary>
    public const int LightfallBase = 8;

    /// <summary>Eula, Lightfall Sword: per Attack the blade counted.
    /// Mirrors <c>C.MC_LIGHTFALL_PER_ATTACK</c>.</summary>
    public const int LightfallPerAttack = 5;

    // THE INAZUMA WORKSHOP'S NUMBERS, on the same terms as the twenty above:
    // every one is that document's own printed text (its sec.3, re-priced in
    // its sec.8), a number the CARD prints stays on the card row, and only a
    // number a POWER carries lands here. Mirrored by value from tier0's `MI_*`
    // block by <c>tools/lint_constant_parity.py</c>.

    /// <summary>Gorou, General's War Banner: the Dexterity it lends and takes
    /// back. Mirrors <c>C.MI_WAR_BANNER_DEXTERITY</c>.</summary>
    public const int WarBannerDexterity = 2;

    /// <summary>Gorou, Juuga: Geo damage per end of turn, 3 turns.
    /// Mirrors <c>C.MI_JUUGA_DMG</c>.</summary>
    public const int JuugaDamage = 6;

    /// <summary>Sayu, Muji-Muji Daruma: the hit above 70% HP.
    /// Mirrors <c>C.MI_DARUMA_DMG</c>.</summary>
    public const int DarumaDamage = 6;

    /// <summary>Sayu, Muji-Muji Daruma: and the Block below it.
    /// Mirrors <c>C.MI_DARUMA_BLOCK</c>.</summary>
    public const int DarumaBlock = 6;

    /// <summary>Kuki Shinobu, Sanctifying Ring: Electro to ALL, per turn.
    /// Mirrors <c>C.MI_SANCTIFYING_RING_DMG</c>.</summary>
    public const int SanctifyingRingDamage = 5;

    /// <summary>Kuki Shinobu, Sanctifying Ring: the Block that rides it.
    /// Mirrors <c>C.MI_SANCTIFYING_RING_BLOCK</c>.</summary>
    public const int SanctifyingRingBlock = 5;

    /// <summary>Thoma, Blazing Barrier: Block per absorbing hit.
    /// Mirrors <c>C.MI_BLAZING_BARRIER_BLOCK</c>.</summary>
    public const int BlazingBarrierBlock = 3;

    /// <summary>Thoma, Crimson Ooyoroi: Pyro per Attack you play.
    /// Mirrors <c>C.MI_OOYOROI_DMG</c>.</summary>
    public const int OoyoroiDamage = 5;

    /// <summary>Thoma, Crimson Ooyoroi: and the Block per Attack.
    /// Mirrors <c>C.MI_OOYOROI_BLOCK</c>.</summary>
    public const int OoyoroiBlock = 3;

    /// <summary>Kujou Sara, Tengu Stormcall: damage your Attacks gain next
    /// turn. Mirrors <c>C.MI_STORMCALL_BONUS</c>.</summary>
    public const int StormcallBonus = 5;

    /// <summary>Yae Miko, Sesshou Sakura: a Sakura's own volley.
    /// Mirrors <c>C.MI_SAKURA_DMG</c>.</summary>
    public const int SakuraDamage = 4;

    /// <summary>Yae Miko, Sesshou Sakura: more, for one placed beside another.
    /// Mirrors <c>C.MI_SAKURA_BONUS</c>.</summary>
    public const int SakuraBonus = 3;

    /// <summary>Yae Miko, Sesshou Sakura: "Up to 3".
    /// Mirrors <c>C.MI_SAKURA_CAP</c>.</summary>
    public const int SakuraCap = 3;

    /// <summary>Yoimiya, Aurous Blaze: the Pyro the mark answers with.
    /// Mirrors <c>C.MI_AUROUS_BLAZE_DMG</c>.</summary>
    public const int AurousBlazeDamage = 6;

    /// <summary>Kamisato Ayaka, Soumetsu: Cryo to ALL, per turn.
    /// Mirrors <c>C.MI_SOUMETSU_DMG</c>.</summary>
    public const int SoumetsuDamage = 8;

    /// <summary>Kamisato Ayaka, Soumetsu: and the hit it ends on.
    /// Mirrors <c>C.MI_SOUMETSU_FINALE</c>.</summary>
    public const int SoumetsuFinale = 16;

    /// <summary>Kamisato Ayato, Kyouka: damage your Attacks gain, 2 turns.
    /// Mirrors <c>C.MI_KYOUKA_BONUS</c>.</summary>
    public const int KyoukaDamage = 4;

    /// <summary>Kamisato Ayato, Kyouka: the illusion that pops at the end.
    /// Mirrors <c>C.MI_KYOUKA_FINALE</c>.</summary>
    public const int KyoukaFinale = 12;

    /// <summary>Kirara, Surprise Dispatch: the parcel, next turn.
    /// Mirrors <c>C.MI_SURPRISE_DISPATCH_DMG</c>.</summary>
    public const int SurpriseDispatchDamage = 10;

    /// <summary>Chiori, Tamoto: Geo per turn, ignoring Block.
    /// Mirrors <c>C.MI_TAMOTO_DMG</c>.</summary>
    public const int TamotoDamage = 6;
}
