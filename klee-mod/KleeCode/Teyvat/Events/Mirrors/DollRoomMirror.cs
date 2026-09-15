using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Audio.Debug;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Extensions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.TestSupport;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// THE DOLL ROOM, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/DollRoom.cs` and cross-checked against
/// the harvest (3 options: Random, Take Some Time, Examine).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same two named `DamageVar`s, the
/// same act-2-ONLY gate, the same ambience started on entry and stopped on
/// every exit, the same three dolls, and the same three options -- one at
/// random for nothing, one of two for 5, one of three for 15.
///
/// THE THREE DOLLS ARE A STATIC TABLE, and it is the base event's: Daughter of
/// the Wind, Mr Struggles and Bing Bong, each with the outcome page it lands
/// on. The page keys go through <see cref="TeyvatEventMirror.PageKey"/> so they
/// re-key per face, which is why the table is built per instance here where
/// the base event can afford a `static readonly` one -- a static table would
/// bake ONE dressing's keys into every face.
///
/// A DOLL OPTION'S KEY IS THE RELIC'S TITLE TEXT. `OptionFromChoice` passes
/// `choice.relic.Title.GetRawText()` as the option's textKey and supplies the
/// title and description LocStrings directly, so the key is not a loc key at
/// all -- it is the metrics/history name, which is also why
/// `WithOverridenHistoryName` follows. Nothing dressed hangs off it and the
/// generator writes no row for it; the words come from the relic's own title
/// and from `pages.TAKE.options.TAKE.description`, which IS dressed and takes
/// a `RelicName` var.
///
/// THE AMBIENCE IS GUARDED BY `LocalContext.IsMe` AND `TestMode.IsOff`, both
/// the base event's: only the local player hears it, and a headless test must
/// not reach the audio manager at all. `StopAudio` is called from the chosen
/// doll AND from `OnEventFinished`, which is what stops the loop when the page
/// is closed any other way.
///
/// THE 5 AND THE 15 ARE PASSED AS THE `DamageVar` ITSELF, not as its value, so
/// the hit carries the var's `Unblockable | Unpowered` props. Passing the
/// number would silently make both blockable.
/// </summary>
public abstract class DollRoomMirror : TeyvatEventMirror
{
    /// <summary>
    /// One doll: the relic it gives and the page it lands on.
    ///
    /// `IComparable&lt;DollChoice&gt;` ON THE RELIC is the base event's, and it is
    /// load-bearing rather than tidiness: `ListExtensions.StableShuffle&lt;T&gt;`
    /// constrains `T` to `IComparable&lt;T&gt;` -- the "stable" in its name is that
    /// it sorts before it shuffles, so the same seed deals the same order
    /// whatever order the list arrived in. Without this the two grid options
    /// would not be reproducible.
    /// </summary>
    private readonly struct DollChoice : IComparable<DollChoice>
    {
        public DollChoice(RelicModel relic, string descriptionKey)
        {
            Relic = relic;
            DescriptionKey = descriptionKey;
        }

        public RelicModel Relic { get; }

        public string DescriptionKey { get; }

        public int CompareTo(DollChoice other) => Relic.CompareTo(other.Relic);
    }

    /// <summary>The base event's own key names.</summary>
    private const string TakeTimeHpLossKey = "TakeTimeHpLoss";

    private const string ExamineHpLossKey = "ExamineHpLoss";

    private int? _ambienceHandle;

    /// <summary>
    /// The base event's three dolls, in its order. PER INSTANCE rather than
    /// `static readonly`, because the description keys go through `PageKey`
    /// and a static table would bake one dressing's entry into every face.
    /// </summary>
    private IReadOnlyList<DollChoice> Dolls => new List<DollChoice>
    {
        new DollChoice(ModelDb.Relic<DaughterOfTheWind>(), PageKey("DAUGHTER_OF_WIND.description")),
        new DollChoice(ModelDb.Relic<MrStruggles>(), PageKey("MR_STRUGGLES.description")),
        new DollChoice(ModelDb.Relic<BingBong>(), PageKey("FABLE.description")),
    };

    private int? AmbienceHandle
    {
        get => _ambienceHandle;
        set
        {
            AssertMutable();
            _ambienceHandle = value;
        }
    }

    /// <summary>`DollRoom.cs:70-74`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DamageVar(TakeTimeHpLossKey, 5m, ValueProp.Unblockable | ValueProp.Unpowered),
            new DamageVar(ExamineHpLossKey, 15m, ValueProp.Unblockable | ValueProp.Unpowered),
        };

    /// <summary>The base event's gate: act 2 ONLY.</summary>
    public override bool IsAllowed(IRunState runState) => runState.CurrentActIndex == 1;

    /// <summary>Three options, in the base event's order, with the damage
    /// annotations on the second and third.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, ChooseRandom, InitialOptionKey("RANDOM")),
            new EventOption(this, TakeSomeTime, InitialOptionKey("TAKE_SOME_TIME"))
                .ThatDoesDamage(DynamicVars[TakeTimeHpLossKey].BaseValue),
            new EventOption(this, Examine, InitialOptionKey("EXAMINE"))
                .ThatDoesDamage(DynamicVars[ExamineHpLossKey].BaseValue),
        };

    /// <summary>The base event's ambience, for the local player and never in a
    /// headless test.</summary>
    protected override Task BeforeEventStarted(bool isPreFinished)
    {
        if (LocalContext.IsMe(Owner) && TestMode.IsOff)
        {
            AmbienceHandle = NDebugAudioManager.Instance.Play("doll_room_amb.mp3");
        }

        return Task.CompletedTask;
    }

    /// <summary>The top option: one doll at random, no damage.</summary>
    private async Task ChooseRandom()
    {
        await ChooseDollAndShowDescription(Rng.NextItem(Dolls.ToArray()));
    }

    /// <summary>The 5, then a choice of two.</summary>
    private async Task TakeSomeTime()
    {
        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature,
            (DamageVar)DynamicVars[TakeTimeHpLossKey], null, null, null);
        IEnumerable<DollChoice> offered = Dolls.ToList().StableShuffle(Rng).Take(2);
        List<EventOption> options = new List<EventOption>();
        foreach (DollChoice choice in offered)
        {
            options.Add(OptionFromChoice(choice));
        }

        SetEventState(L10NLookup(PageKey("TAKE_SOME_TIME.description")), options);
    }

    /// <summary>The 15, then a choice of all three.</summary>
    private async Task Examine()
    {
        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature,
            (DamageVar)DynamicVars[ExamineHpLossKey], null, null, null);
        IEnumerable<DollChoice> offered = Dolls.ToList().StableShuffle(Rng);
        List<EventOption> options = new List<EventOption>();
        foreach (DollChoice choice in offered)
        {
            options.Add(OptionFromChoice(choice));
        }

        SetEventState(L10NLookup(PageKey("EXAMINE.description")), options);
    }

    /// <summary>
    /// One doll on the grid: the relic's own title, the shared TAKE
    /// description with the relic's name slotted in, and the relic's TITLE TEXT
    /// as the option's metrics key -- the base event's own, see the class
    /// comment.
    /// </summary>
    private EventOption OptionFromChoice(DollChoice choice)
    {
        LocString title = choice.Relic.Title;
        LocString description = L10NLookup(PageKey("TAKE.options.TAKE.description"));
        description.Add("RelicName", choice.Relic.Title);
        return new EventOption(
            this, Take, title, description, choice.Relic.Title.GetRawText(),
            HoverTipFactory.FromRelic(choice.Relic))
            .WithOverridenHistoryName(choice.Relic.Title);

        Task Take() => ChooseDollAndShowDescription(choice);
    }

    /// <summary>The ambience stops FIRST, then the relic, then the doll's own
    /// page.</summary>
    private async Task ChooseDollAndShowDescription(DollChoice choice)
    {
        StopAudio();
        await RelicCmd.Obtain(choice.Relic.ToMutable(), Owner);
        SetEventFinished(L10NLookup(choice.DescriptionKey));
    }

    /// <summary>The second place the ambience stops: any other way out.</summary>
    protected override void OnEventFinished()
    {
        StopAudio();
    }

    private void StopAudio()
    {
        if (AmbienceHandle.HasValue)
        {
            NDebugAudioManager.Instance.Stop(AmbienceHandle.Value);
            AmbienceHandle = null;
        }
    }
}
