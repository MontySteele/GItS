using Godot;
using KleeMod.Tests.Harness;
using Xunit;

namespace KleeMod.Tests;

/// <summary>
/// The card reward row probe's judgement, pinned. The probe itself needs a
/// scene tree, which this host cannot build; what it decides is plain
/// rectangle arithmetic, so that part is tested here, together with the row
/// geometry the probe's header argues from (350 px apart, centred, a 240 px
/// card at the row's 0.8 scale, a 1920 px canvas at 16:9).
/// </summary>
public class RewardRowProbeTests
{
    private const float Spacing = 350f;
    private const float CardW = 240f;
    private const float CardH = 337.6f;

    private static string Classify(Rect2 view, Rect2 card, bool visible) =>
        Il.Method("RewardRowProbe", "Classify")
          .Invoke(null, new object[] { view, card, visible })!.ToString()!;

    private static float ExpectedX(int index, int count) =>
        (float)Il.Method("RewardRowProbe", "ExpectedX")
                 .Invoke(null, new object[] { index, count })!;

    /// <summary>A card of the row's size centred at (x, y) on the canvas.</summary>
    private static Rect2 CardAt(float x, float y) =>
        new(x - CardW / 2f, y - CardH / 2f, CardW, CardH);

    private static readonly Rect2 View169 = new(0f, 0f, 1920f, 1080f);

    [Fact]
    public void A_card_inside_the_canvas_is_on_screen()
    {
        Assert.Equal("OnScreen", Classify(View169, CardAt(960f, 616f), true));
    }

    [Fact]
    public void A_card_touching_the_edge_exactly_is_on_screen()
    {
        Assert.Equal("OnScreen", Classify(View169, new Rect2(1680f, 400f, CardW, CardH), true));
    }

    [Fact]
    public void A_card_across_the_edge_is_partly_off()
    {
        Assert.Equal("PartlyOff", Classify(View169, CardAt(1900f, 616f), true));
    }

    [Fact]
    public void A_card_past_the_edge_is_off_screen()
    {
        Assert.Equal("OffScreen", Classify(View169, CardAt(2400f, 616f), true));
        Assert.Equal("OffScreen", Classify(View169, CardAt(-400f, 616f), true));
    }

    [Fact]
    public void A_hidden_or_shrunk_card_is_not_drawn()
    {
        Assert.Equal("NotDrawn", Classify(View169, CardAt(960f, 616f), false));
        Assert.Equal("NotDrawn", Classify(View169, new Rect2(960f, 616f, 0f, 0f), true));
    }

    [Fact]
    public void The_expected_row_is_centred_and_350_apart()
    {
        Assert.Equal(-350f, ExpectedX(0, 3));
        Assert.Equal(0f, ExpectedX(1, 3));
        Assert.Equal(350f, ExpectedX(2, 3));
        Assert.Equal(-525f, ExpectedX(0, 4));
        Assert.Equal(525f, ExpectedX(3, 4));
    }

    /// <summary>
    /// The header's claim, as numbers: on a 16:9 canvas the base layout keeps
    /// three, four and five cards on screen and first runs off at six. A
    /// four-card reward (three plus the companion) is never off screen by the
    /// row arithmetic alone.
    /// </summary>
    [Theory]
    [InlineData(3, true)]
    [InlineData(4, true)]
    [InlineData(5, true)]
    [InlineData(6, false)]
    public void The_base_row_fits_a_16_by_9_canvas_up_to_five_cards(int count, bool fits)
    {
        var allOn = true;
        for (var i = 0; i < count; i++)
        {
            var card = CardAt(960f + ExpectedX(i, count), 616f);
            allOn &= Classify(View169, card, true) == "OnScreen";
        }
        Assert.Equal(fits, allOn);
        Assert.Equal(Spacing, ExpectedX(1, 2) - ExpectedX(0, 2));
    }
}
