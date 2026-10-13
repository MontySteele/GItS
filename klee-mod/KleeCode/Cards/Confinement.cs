using Godot;

namespace KleeMod.Cards;

/// <summary>
/// CONFINEMENT, Klee's own Curse (Klee story batch 1 sec.3,
/// <c>review/ruled/klee-story-batch-1-2026-10-12.md</c>): "Unplayable. After
/// 3 combats, remove this from your deck." Jean always lets her out
/// eventually. A <see cref="StoryCurse"/>, which holds the clock.
///
/// ONLY STARSNATCH CLIFF GIVES IT. It sits in Klee's pool on the
/// never-generated list (<see cref="KleeOffPoolCards"/>).
/// </summary>
public sealed class Confinement : StoryCurse
{
    public const string TitleText = "Confinement";

    protected override string CurseTitle => TitleText;

    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("proto_ko_sorry_jean");
}
