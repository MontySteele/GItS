using System;
using Godot;
using HarmonyLib;
using KleeMod.Cards;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Cards;

namespace KleeMod.Vfx;

/// <summary>
/// THE ELEMENT INDICATOR -- the element a card applies, drawn on its face
/// instead of written under its rules.
///
/// [USER], 2026-09-01, after playing Klee: "instead of saying 'applies pyro' -
/// maybe make it a card indicator as well to remove text overhead? That would
/// be a universal shift."
///
/// WHAT THE SENTENCE WAS. Not codegen text: no sheet row and no generated
/// `Localization` ever contained the words. `KleeKeywords.AppliesPyro` and its
/// three siblings were registered with
/// <c>AutoKeywordPosition.After</c>, which puts a keyword into BaseLib's
/// <c>AutoKeywordText.AdditionalAfterKeywords</c> and from there into the
/// base game's own <c>CardKeywordOrder.afterDescription</c> -- so
/// <c>CardModel.BuildDescription</c> appended "Applies Pyro" as a line of the
/// rules box on every face carrying the keyword. Flipping those four fields to
/// <c>AutoKeywordPosition.None</c> is the whole of the removal, and it is ONE
/// switch for all 114 faces across the four sheets and both quarantined arms,
/// because there is one keyword per element and every sheet declares the same
/// four.
///
/// WHAT THE PLAYER LOSES AND DOES NOT. The TIP is untouched.
/// <c>CardModel.HoverTips</c> walks <c>Keywords</c> and calls
/// <c>HoverTipFactory.FromKeyword</c> on every one of them; it never reads the
/// printed text. So `Applies Pyro` still hovers with the aura duration and the
/// reaction rule in it, exactly as it did, and the board-aware reaction
/// previews beside it (<see cref="KleeCardTooltips.ForCard"/>) are untouched
/// too. `Bomb`, `Confiscated` and the eight previews have ridden
/// <c>AutoKeywordPosition.None</c> since they were written, which is the proof
/// that a tip survives the position: they have never printed a line and have
/// always hovered.
///
/// THE SEAM: THE TYPE PLAQUE. `%TypePlaque` is the base game's own per-card
/// classification badge -- the pill reading "Attack" / "Skill" / "Power",
/// centred on the divider between the portrait and the rules box. It is the
/// one place on a StS2 card that already answers "what KIND of card is this?",
/// which is the question an element answers a second time. So the gem sits
/// immediately to the plaque's LEFT, vertically centred on it, and the pair
/// reads as one classification: a flame and the word Attack.
///
/// IT IS A CHILD OF THE PLAQUE, WITH ANCHORS, AND THAT IS THE WHOLE GEOMETRY.
/// `UpdateTypePlaqueSizeAndPosition` re-sizes the plaque to its label and
/// re-centres it, DEFERRED -- so any code that reads the plaque's rect at
/// patch time reads a stale one, and a badge positioned from that number
/// would jump by the width difference between "Attack" and "Power". Anchoring
/// to the parent instead makes the engine do the recompute at layout time:
/// <c>AnchorLeft = AnchorRight = 0</c> pins the gem to the plaque's left edge,
/// <c>AnchorTop = AnchorBottom = 0.5</c> to its vertical middle, and the four
/// offsets below are the only numbers in this file. (This is the opposite call
/// from <see cref="Prototype.KurageMemoryPileRing"/>, deliberately: its parent
/// is the `NCard` itself, a Node2D with no rect for an anchor to resolve
/// against, so there the anchors are the bug and an explicit rect is the fix.)
///
/// THE ICON IS THE AURA'S OWN. `klee/powers/aura_&lt;element&gt;.png` is the
/// texture <see cref="Powers.KleePowerIcons"/> already gives
/// <see cref="Powers.AuraPower"/>, i.e. the badge that will appear ON THE
/// ENEMY when this card lands. Card and consequence are literally the same
/// picture, which is the affordance the sentence never gave; and the four are
/// separated by SILHOUETTE (flame, droplet, bolt, snowflake) as well as by
/// hue, the <see cref="MeterCostBadge"/> rule, because hue is what a busy
/// board and a colour-blind player lose first.
///
/// ANEMO AND GEO GET NO GEM, and that is not an omission: they leave no aura
/// (LAW, combat sec.: "Anemo/Geo leave no aura -- they only trigger"), so there
/// is no aura icon to draw and they never printed a sentence either. The
/// indicator says exactly what the sentence said, no more.
///
/// `EB-454` GAVE THEM THE KEYWORD ANYWAY, and the split is the point: the two
/// now carry `KleeKeywords.AppliesAnemo` / `AppliesGeo` -- so they hover a tip
/// and print `[Anemo]` on the blind page -- while <see cref="AuraElements"/>
/// and <see cref="IconPathFor"/> stay four, so nothing here paints anything
/// new. The word is not the picture: the r13 seat read `Jean -- Gale Blade` as
/// untyped for a whole fight, which is a complaint about the word.
/// </summary>
internal static class ElementBadge
{
    /// <summary>The node's name on the plaque, so a pooled `NCard` reuses the
    /// one it already carries instead of stacking a second.</summary>
    internal const string NodeName = "KleeElementBadge";

    /// <summary>The plaque, by its scene-unique name -- what `NCard._Ready`
    /// itself resolves, so the two cannot drift, and a scene that no longer
    /// carries it makes this inert instead of throwing. The
    /// <see cref="NonFiniteCardGuard"/> reads it the same way and says so.
    /// </summary>
    internal const string PlaquePath = "%TypePlaque";

    /// <summary>The gem's side, in the card's own pixels (`NCard.defaultSize`
    /// is 300x422, so this is a sixth of the card's width). Sized against the
    /// energy orb rather than against the plaque: it is a second cost-grade
    /// affordance, not a second word.</summary>
    internal const float Side = 48f;

    /// <summary>The gap between the gem's right edge and the plaque's left.
    /// Wide enough that the pair reads as two things, tight enough that it
    /// reads as one row.</summary>
    internal const float Gap = 10f;

    /// <summary>
    /// The elements that leave an aura, in the order a face is read for them.
    ///
    /// ORDER IS LOAD-BEARING because a face may carry TWO: a companion whose
    /// own element is one thing and whose printed `apply_aura` is another
    /// (codegen's `aura_elements` list, which is what emits the keywords).
    /// The gem draws the FIRST, which is the card's OWN element -- the one its
    /// damage carries -- and the second stays where it always was, in the
    /// rules text that names it and in its own hover tip. A row of two gems
    /// was considered and refused: the whole point of the change is less on
    /// the face, not the same amount in pictures.
    /// </summary>
    private static readonly Element[] AuraElements =
    {
        Element.Pyro, Element.Hydro, Element.Electro, Element.Cryo,
    };

    /// <summary>
    /// The element this card's face declares, or <c>Element.None</c>.
    ///
    /// READ OFF THE KEYWORD, not off <see cref="IElementalCard"/> and not off
    /// a second list. The keyword is what the tip is built from
    /// (<c>CardModel.HoverTips</c>) and what codegen emits from the sheet's
    /// cadence rule, so asking it makes the gem and the tip one declaration:
    /// a card can no more wear a gem it does not explain than it can explain
    /// an element it does not wear. `IElementalCard` would have been the
    /// wrong source in both directions -- it is absent on an apply-only skill,
    /// and it carries `Element.None` for the one companion row that declares
    /// no element at all (Kirara, Dendro, which this engine has no aura for).
    /// </summary>
    internal static Element ElementOf(CardModel card)
    {
        var keywords = card.Keywords;
        foreach (var element in AuraElements)
        {
            var keyword = KleeKeywords.AuraApplication(element);
            if (keyword != CardKeyword.None && keywords.Contains(keyword))
            {
                return element;
            }
        }

        return Element.None;
    }

    /// <summary>
    /// The pck-relative texture for an element, or null where it leaves no
    /// aura. Pure -- no loader, no node -- so the declaration is the half a
    /// headless test can reach, the <see cref="MeterCostBadge.IconPathFor"/>
    /// split and for the same reason.
    /// </summary>
    internal static string? IconPathFor(Element element)
        => element switch
        {
            Element.Pyro => "klee/powers/aura_pyro.png",
            Element.Hydro => "klee/powers/aura_hydro.png",
            Element.Electro => "klee/powers/aura_electro.png",
            Element.Cryo => "klee/powers/aura_cryo.png",
            _ => null,
        };

    private static bool _warnedFreedGlyph;

    /// <summary>
    /// The gem's texture, RESOLVED FRESH ON EVERY PAINT (EB-222).
    ///
    /// The rule this file inherits whole from <see cref="MeterCostBadge"/>:
    /// the game preloads a room's asset set and TEARS IT DOWN with the room,
    /// so a `Texture2D` held in a static of ours is a corpse by the first card
    /// of the next combat and `TextureRect.SetTexture` throws
    /// `ObjectDisposedException` out of the turn loop. Ask `ResourceLoader`
    /// each time -- it answers a second load of a live path from the engine's
    /// own cache -- and check the answer, because a cache we do not own can
    /// hand back a wrapper for an object that is already gone.
    /// </summary>
    private static Texture2D? Glyph(Element element, out bool freed)
    {
        freed = false;

        string? declared = IconPathFor(element);
        string? path = declared == null ? null : KleePck.Path(declared);
        if (path == null)
        {
            return null;
        }

        Texture2D? texture = ResourceLoader.Load<Texture2D>(path);
        if (texture == null)
        {
            return null;
        }

        if (!GodotObject.IsInstanceValid(texture))
        {
            freed = true;
            return null;
        }

        return texture;
    }

    private static void WarnFreedGlyph(string detail)
    {
        if (_warnedFreedGlyph)
        {
            return;
        }

        _warnedFreedGlyph = true;
        Log.Warn($"[{KleeMod.ModId}] element badge: the element glyph was freed "
               + $"by the engine ({detail}); the card draws without its gem.");
    }

    /// <summary>
    /// Put the element on the card, or take it off -- and never, under any
    /// circumstance, throw at the caller.
    ///
    /// `Paint` runs from `UpdateStarCostVisuals`, i.e. INSIDE THE TURN LOOP
    /// (`CardPileCmd.Draw` redraws every card it moves), and EB-222 is what an
    /// exception from here costs: the loop dies, the combat is stuck, and the
    /// run is over. So every early return below is a real case and the write
    /// itself is wrapped.
    ///
    /// EVERY EARLY RETURN IS A REAL CASE. A null model or an unready node is
    /// the pooled-`NCard` lifecycle; a card with no `Applies` keyword is every
    /// base-game card and every skill of ours that applies nothing; and a
    /// missing plaque is a card scene the game has changed under us.
    /// </summary>
    internal static void Paint(NCard nCard)
    {
        CardModel? card = nCard.Model;
        if (card == null || !nCard.IsNodeReady())
        {
            return;
        }

        // `IsNodeReady` ON THE PLAQUE TOO, and it is not caution: it is the
        // branch `AddChildSafely` takes. An unready parent gets a DEFERRED
        // `AddChild`, so a second paint in the same frame would find no gem
        // yet, build a second, and leave the card wearing two -- Godot renames
        // the duplicate rather than refusing it, so the fault would be silent.
        // Waiting one paint costs nothing; the hook fires on every redraw.
        var plaque = nCard.GetNodeOrNull<Control>(PlaquePath);
        if (plaque == null || !plaque.IsNodeReady())
        {
            return;
        }

        var gem = plaque.GetNodeOrNull<TextureRect>(NodeName);

        // The element, every paint rather than only on creation: a pooled
        // `NCard` reaches us carrying whatever the last card left on it, and a
        // Pyro gem on a Hydro card is worse than no gem at all.
        var element = ElementOf(card);
        Texture2D? texture = null;
        if (element != Element.None)
        {
            texture = Glyph(element, out bool freed);
            if (freed)
            {
                // A degrade, never a throw -- the EB-221 shape. The card draws
                // without its gem and the keyword tip still explains the aura.
                WarnFreedGlyph("IsInstanceValid was false for the loaded texture");
            }
        }

        if (texture == null)
        {
            Hide(gem);
            return;
        }

        if (gem == null)
        {
            gem = Build();
            plaque.AddChildSafely(gem);
        }

        Show(gem, texture);
    }

    /// <summary>
    /// The gem node, anchored to the plaque. The four offsets are the only
    /// geometry in this file; see the class note for why they are offsets and
    /// not a rect.
    /// </summary>
    private static TextureRect Build() => new()
    {
        Name = NodeName,
        // The gem is decoration over a plaque the player never clicks; a
        // filter of anything else would eat the card's own hover, which is
        // what raises the tip that explains the gem.
        MouseFilter = Control.MouseFilterEnum.Ignore,
        ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
        StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
        AnchorLeft = 0f,
        AnchorRight = 0f,
        AnchorTop = 0.5f,
        AnchorBottom = 0.5f,
        OffsetLeft = -(Gap + Side),
        OffsetRight = -Gap,
        OffsetTop = -Side / 2f,
        OffsetBottom = Side / 2f,
    };

    private static void Show(TextureRect gem, Texture2D texture)
    {
        try
        {
            if (!GodotObject.IsInstanceValid(gem))
            {
                return;
            }

            gem.Texture = texture;
            gem.Visible = true;
        }
        catch (ObjectDisposedException e)
        {
            WarnFreedGlyph(e.Message);
        }
    }

    private static void Hide(TextureRect? gem)
    {
        try
        {
            if (gem != null)
            {
                gem.Visible = false;
            }
        }
        catch (ObjectDisposedException)
        {
            // The node itself is gone. Nothing to hide, and nothing further to
            // do: the next paint builds a fresh one on a fresh plaque.
        }
    }
}

/// <summary>
/// The one arming point, deliberately the same hook <see cref="MeterCostBadge"/>
/// and the Kurage queue ring use: `UpdateStarCostVisuals` is called from
/// `UpdateVisuals` and `SetPretendCardCanBePlayed`, i.e. from every redraw the
/// game already performs, on every surface that renders a card -- hand, draw
/// pile, reward, shop, compendium. So the gem refreshes on exactly the cadence
/// the cost badges do and needs no polling of its own.
///
/// NOT `UpdateTypePlaque`, even though the plaque is the parent: that method
/// defers the sizing pass, so a postfix on it runs BEFORE the plaque has its
/// final rect. The gem is anchored rather than positioned precisely so the
/// arming point does not have to care.
/// </summary>
[HarmonyPatch(typeof(NCard), "UpdateStarCostVisuals")]
internal static class NCard_UpdateStarCostVisuals_KleeElementBadge_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NCard __instance) => ElementBadge.Paint(__instance);
}
