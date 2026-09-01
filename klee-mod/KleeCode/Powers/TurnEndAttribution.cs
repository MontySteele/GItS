using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// WHAT THE END OF YOUR TURN IS ABOUT TO DO, named and numbered (EB-53/N1 —
/// the attribution pass).
///
/// THE DEFECT THIS EXISTS FOR. Playtest 4: "off-seat bursts are invisible
/// inside end-of-turn noise", and the Bake-Kurage pulse "resolves at END OF
/// TURN, from a bank that will have moved by then, so the summon card's face
/// can never print it" (<see cref="Cards.KokomiRiderTips"/>). Four separate
/// effects can fire per creature per end of turn, in one burst of numbers,
/// with nothing on screen saying which creature or which effect produced any
/// of them.
///
/// THE ORDER IS DEFINED HERE, ONCE, AND <see cref="TurnEndSequencer"/> DRIVES
/// IT. Before this file the sequencer carried the order as four hand-written
/// statements and any preview would have carried a fifth, hand-written copy —
/// which is precisely the drift the Furina legibility sprint legislated
/// against (a preview and an effect that compute separately will eventually
/// disagree, and the player believes the preview). A preview built from a
/// second list would be able to name the volleys in an order the sequencer no
/// longer fires them in. So the table below is the single source of BOTH: the
/// resolution walks <see cref="Order"/> and so does the display.
///
/// The sequence itself is unchanged and still LAW — tier0
/// `effects.player_turn_end_triggers`, read top to bottom:
///
///     masque_red_death  (Bond of Life, `p.block -= paid`)
///     sparks_n_splash   (Pyro volley)
///     oz_summon         (Electro volley)
///     kurage_summon     (Hydro pulse + Block)
///
/// EVERY PREVIEW READ IS THE RESOLUTION'S OWN ACCESSOR. The Kurage number
/// comes from <see cref="KurageSummonPower.PulseDamage"/>, the same static the
/// hit calls and the same one <see cref="Cards.KokomiRiderTips"/> already
/// quotes; the volleys quote the constants their loops iterate. Nothing here
/// re-derives arithmetic, so a chip cannot disagree with the hit.
///
/// PREVIEWS ARE PURE. Not one accessor below mutates state, latches a
/// per-turn window, or touches <c>Rng.CombatTargets</c> — the ruling in
/// <see cref="PreventExhaustWardPower"/>, where a preview that armed a latch
/// desynced a co-op table on 2026-07-27 and got a client disconnected. A
/// preview is a question about the current board; asking it a different number
/// of times on each peer must cost nothing.
///
/// WHAT A PREVIEW CANNOT PROMISE, stated rather than hidden: the volleys pick
/// RANDOM targets and resolve through <see cref="ElementalHit"/>, which applies
/// Strength, Weak and Vulnerable per target. There is no target to read before
/// the turn ends, so the volley chips quote the SOURCE number — what the power
/// itself deals — not the number that will land on a specific enemy. The hover
/// copy says so. The Kurage chip is exact in the other direction: its whole
/// variable is the Charge bank, which the preview reads live.
/// </summary>
public sealed class TurnEndSource
{
    /// <summary>Stable key, used by the display for its per-slot state.</summary>
    public required string Key { get; init; }

    /// <summary>Loc key stem for the hover title (see KleeMod.InjectLocStrings).</summary>
    public required string TitleKey { get; init; }

    /// <summary>
    /// pck-relative sprite for the ENTITY, when the source has a body on the
    /// field rather than only a badge. Null falls through to the power's own
    /// icon via <see cref="KleePowerIcons"/>, so three of the four sources
    /// need no new art at all.
    /// </summary>
    public string? SpritePath { get; init; }

    /// <summary>The live power instance on this creature, or null if the
    /// source is not standing. One lookup serves presence, duration, icon and
    /// numbers, so they cannot describe different instances.</summary>
    public required Func<Creature, PowerModel?> Find { get; init; }

    /// <summary>The number this source is about to produce, as the chip prints
    /// it. Read through the resolution's own accessor — never re-derived.</summary>
    public required Func<Creature, string> Preview { get; init; }

    /// <summary>Is the previewed number ABOVE the rate the source's printed
    /// text quotes? Renders in the game's modified-value colour, the
    /// SalonVisualsBridge chip rule.</summary>
    public required Func<Creature, bool> Buffed { get; init; }

    /// <summary>Hover copy. Same discipline as SalonMemberTips: written once,
    /// numbers from the constants, so a repricing cannot leave it quoting a
    /// retired figure.</summary>
    public required Func<Creature, string> Body { get; init; }

    /// <summary>Resolution. Lifted verbatim out of the sequencer's four
    /// hand-written statements — same power type, same method, same ToList()
    /// re-read across the await.</summary>
    public required Func<Creature, PlayerChoiceContext, Task> Resolve { get; init; }

    /// <summary>Turns the source has left, 0 when it is not a duration.</summary>
    public Func<Creature, int>? TurnsLeft { get; init; }
}

/// <summary>The table. See <see cref="TurnEndSource"/> for why it is one
/// table and not two lists.</summary>
public static class TurnEndAttribution
{
    public const string MasqueKey = "KLEEMOD-TURNEND_MASQUE";
    public const string SparksKey = "KLEEMOD-TURNEND_SPARKS";
    public const string OzKey = "KLEEMOD-TURNEND_OZ";
    public const string KurageKey = "KLEEMOD-TURNEND_KURAGE";

    /// <summary>
    /// The Bake-Kurage entity, cut from the summon art by
    /// tools/cut_kurage_summon.py (art_lint L11 GENERATOR_OWNED). This is the
    /// one source whose slot renders a CREATURE rather than a badge, because
    /// it is the one source that is a creature — the Salon stage's members are
    /// the precedent, and the ask (EB-53/N1) is "render the summon entity".
    ///
    /// Wiring the path ahead of the asset is deliberate and already ruled:
    /// KleePck.Path returns null while a file is absent, the sprite stays
    /// hidden, and the chip with the number renders anyway. Unlike the power
    /// badges of EB-65 there is no base-game getter to fall through to, so an
    /// absent file cannot produce a NOPE placeholder here — it produces a
    /// number with no picture, which is the degradation we want.
    /// </summary>
    private const string KurageSprite = "kokomi/summon/bake_kurage.png";

    private static PowerModel? First<T>(Creature creature) where T : PowerModel =>
        creature.Powers.OfType<T>().FirstOrDefault();

    private static int Amount<T>(Creature creature) where T : PowerModel =>
        (int)(First<T>(creature)?.Amount ?? 0);

    /// <summary>
    /// tier0 `effects.player_turn_end_triggers`, top to bottom. Reordering
    /// this list reorders the game — see TurnEndSequencer's header for the two
    /// filed races (races-a: the Bond eats Block the pulse would have granted;
    /// races-c: volley order picks which reactions fire AND the order of draws
    /// from the shared Rng.CombatTargets stream).
    /// </summary>
    public static readonly IReadOnlyList<TurnEndSource> Order = new TurnEndSource[]
    {
        new()
        {
            Key = "masque",
            TitleKey = MasqueKey,
            Find = First<MasqueRedDeathPower>,
            TurnsLeft = static _ => 0,
            // What the Bond will actually take, which is capped by the Block
            // standing right now. Quoting the flat constant would promise a
            // payment a 2-Block creature cannot make.
            Preview = static creature =>
                $"-{Math.Min((int)creature.Block, CompanionConstants.MasqueBondBlock)}",
            Buffed = static _ => false,
            Body = static creature =>
                $"[gold]Bond of Life[/gold] consumes the first "
              + $"{CompanionConstants.MasqueBondBlock} Block you gain each "
              + $"turn, and it is paid FIRST — before anything else here can "
              + $"grant Block. You hold {(int)creature.Block}: it will take "
              + $"{Math.Min((int)creature.Block, CompanionConstants.MasqueBondBlock)}.",
            Resolve = static async (creature, choiceContext) =>
            {
                foreach (var masque in creature.Powers
                             .OfType<MasqueRedDeathPower>().ToList())
                {
                    await masque.PayBondOfLife(choiceContext);
                }
            },
        },
        new()
        {
            Key = "sparks",
            TitleKey = SparksKey,
            Find = First<SparksNSplashPower>,
            TurnsLeft = Amount<SparksNSplashPower>,
            Preview = static _ =>
                $"{KitBurstConstants.VolleyHits}x{KitBurstConstants.VolleyHitDamage}",
            Buffed = static _ => false,
            Body = static creature =>
                $"[gold]Sparks 'n' Splash[/gold] (Burst): "
              + $"{KitBurstConstants.VolleyHits} hits of "
              + $"{KitBurstConstants.VolleyHitDamage}, each to a RANDOM enemy, "
              + $"each applying [gold]Pyro[/gold]. Fires FIRST of the three "
              + $"volleys. Lasts {Amount<SparksNSplashPower>(creature)} more "
              + "turn(s). The targets are not chosen until the turn ends, so "
              + "Strength and Vulnerable are not in this number.",
            Resolve = static async (creature, choiceContext) =>
            {
                foreach (var pyro in creature.Powers
                             .OfType<SparksNSplashPower>().ToList())
                {
                    await pyro.FireVolley(choiceContext);
                }
            },
        },
        new()
        {
            Key = "oz",
            TitleKey = OzKey,
            Find = First<OzSummonPower>,
            TurnsLeft = Amount<OzSummonPower>,
            Preview = static _ => CompanionConstants.OzDamage.ToString(),
            Buffed = static _ => false,
            Body = static creature =>
                $"[gold]Oz, at Your Side[/gold]: {CompanionConstants.OzDamage} "
              + "damage and [gold]Electro[/gold] to a RANDOM enemy. Fires "
              + "SECOND of the three volleys. Lasts "
              + $"{Amount<OzSummonPower>(creature)} more turn(s). The target is "
              + "not chosen until the turn ends, so Strength and Vulnerable "
              + "are not in this number.",
            Resolve = static async (creature, choiceContext) =>
            {
                foreach (var electro in creature.Powers
                             .OfType<OzSummonPower>().ToList())
                {
                    await electro.FireVolley(choiceContext);
                }
            },
        },
        new()
        {
            Key = "kurage",
            TitleKey = KurageKey,
            SpritePath = KurageSprite,
            Find = First<KurageSummonPower>,
            TurnsLeft = Amount<KurageSummonPower>,
#if PROTOTYPE_CARDS
            // `EB-247`. QUARANTINED, and it is this whole docket row that
            // moves. Under the memory rule `PulseDamage` and `PulseMultiplier`
            // are the retired arithmetic -- the pulse reads the bank not at
            // all -- so the chip previewed a number the hit does not deal and
            // flagged it "raised" off an amp that no longer amplifies
            // anything. The preview reads the same forecast the wire and the
            // fielding tip do, through `KurageMemory.Forecast`.
            Preview = static creature =>
            {
                var (kind, _, amount) = KurageMemory.Forecast(creature);
                return kind == "none" ? "-" : amount.ToString();
            },
            // NOTHING RAISES THIS PULSE ANY MORE. Every branch is a flat law
            // constant, so the chip has no amped state to mark, and claiming
            // one would be the same class of falsehood as the number above.
            Buffed = static _ => false,
            // NO DURATION SENTENCE. Same fact `EB-197` settled on the buff
            // itself: the stacks are clamped to 1 and never tick, so "Lasts N
            // more turn(s)" was a countdown the power does not have -- and
            // this was the one surface still appending it.
            Body = static creature =>
                Cards.KokomiRiderTips.PulseBody(creature, inCombat: true),
#else
            // THE ASK, literally: the pulse's damage, before end of turn,
            // through the accessor the hit uses.
            Preview = static creature =>
                KurageSummonPower.PulseDamage(creature).ToString(),
            // CLOSES THE GAP KurageAmpPower FLAGGED. Its own summary records
            // that "a player holding two copies sees the Bake-Kurage text
            // quote the unamped number while the hit uses the amped one",
            // because Localization resolves on the canonical model with no
            // owner to read an amp off. This chip has an owner, so it shows
            // the amped number AND marks it as raised.
            Buffed = static creature =>
                KurageSummonPower.PulseMultiplier(creature)
                > KokomiConstants.KuragePulsePerCharge,
            Body = static creature =>
                Cards.KokomiRiderTips.PulseBody(creature, inCombat: true)
              + $" Lasts {Amount<KurageSummonPower>(creature)} more turn(s).",
#endif
            Resolve = static async (creature, choiceContext) =>
            {
                foreach (var hydro in creature.Powers
                             .OfType<KurageSummonPower>().ToList())
                {
                    await hydro.FirePulse(choiceContext);
                }
            },
        },
    };

    /// <summary>
    /// The sources standing on this creature RIGHT NOW, in firing order.
    /// Pure: a lookup and a filter, nothing else.
    /// </summary>
    public static IReadOnlyList<TurnEndSource> Standing(Creature? creature)
    {
        if (creature == null) return Array.Empty<TurnEndSource>();
        return Order.Where(source => source.Find(creature) != null).ToList();
    }
}
