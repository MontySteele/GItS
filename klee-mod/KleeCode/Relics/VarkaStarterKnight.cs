using BaseLib.Utils;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Entities.Players;

namespace KleeMod.Relics;

/// <summary>
/// THE RUN'S STARTER KNIGHT ELEMENT, recorded when Boreas's Fang rolls the
/// Knight (<see cref="BoreasFang.AfterObtained"/>) and saved with the Fang, so
/// Knight's Commission reads the rolled element for the whole run even after
/// the card is removed or transformed (main session, 2026-10-01). A BaseLib
/// <c>SavedSpireField</c> on the Fang: it is written into the Fang's saved
/// properties and read back on a load, matched by <c>IsInstanceOfType</c>, so
/// Wolf's Gravestone (a Fang) carries it too; the Touch of Orobas hand-over
/// copies it (<see cref="BoreasFang.GetUpgradeReplacement"/>).
///
/// A run begun before this field existed reads 0, <see cref="Element.None"/>,
/// and Knight's Commission falls back to the starter Knight in the deck.
/// Its own file so the parallel card branch's edits cannot collide with it.
/// </summary>
public static class VarkaStarterKnight
{
    private static readonly SavedSpireField<BoreasFang, int> Saved =
        new(() => (int)Element.None, "KleeMod_VarkaStarterKnightElement");

    /// <summary>The element this Fang recorded, or None.</summary>
    public static Element Of(BoreasFang? fang) =>
        fang == null ? Element.None : (Element)Saved.Get(fang);

    /// <summary>The element the run rolled for this player, or None.</summary>
    public static Element Of(Player? player) => Of(BoreasFang.HeldBy(player));

    /// <summary>Record the rolled element on this Fang.</summary>
    public static void Record(BoreasFang fang, Element element) =>
        Saved.Set(fang, (int)element);
}
