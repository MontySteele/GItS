using System.Collections.Generic;
using BaseLib.Utils.NodeFactories;
using Godot;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Teyvat;

/// <summary>
/// THE FACTORY BaseLib DOES NOT SHIP, for the one type an act dressing needs.
///
/// BaseLib's `NodeFactory.Init` constructs six factories -- `ControlFactory`,
/// `NCreatureVisualsFactory`, `NRestSiteCharacterFactory`,
/// `NMerchantCharacterFactory`, `NEnergyCounterFactory` and
/// `NCustomTreasureRoomChestFactory` -- and `TryAutoConvert` refuses, with
/// "registered for X but no factory exists for that type", for anything else.
/// `NCombatBackground` is something else, so registering our background root
/// for conversion without this class would fail exactly as loudly and exactly
/// as uselessly as not registering it at all.
///
/// WHAT IT HAS TO GET RIGHT, and it is one thing: the six child nodes
/// `NCombatBackground.AddLayer` fetches with `GetNodeOrNull` and throws on
/// (`NCombatBackground.cs:82`) must end up as direct children OF THE
/// CONVERTED ROOT, not of the source root hung underneath it.
/// `NodeFactory&lt;T&gt;.TransferAndCreateNodes` picks between those two
/// shapes on `FlexibleStructure`, which is `NamedNodes.All(i =&gt; i.UniqueName)`
/// -- true for an EMPTY list and for an all-`%` list, and true means "add the
/// source as a child" rather than "move the children across". Declaring all
/// six by their PLAIN names is therefore load-bearing twice over: it forces
/// the transfer branch, and it makes a scene that is missing a layer node
/// self-heal through <see cref="GenerateNode"/> instead of throwing in the
/// middle of a combat's first frame.
///
/// `MakeNameUnique: false` because the base game's own background scenes do
/// not mark these nodes unique and `AddLayer` looks them up by plain relative
/// path; a `%` lookup is never made against them.
/// </summary>
internal sealed class NCombatBackgroundFactory : NodeFactory<NCombatBackground>
{
    /// <summary>
    /// The layer slots, in `AddLayer`'s own spelling
    /// (<c>$"Layer_{i:D2}"</c> for each chosen `_bg_NN` group, then
    /// `"Foreground"`). Five plus one, matching `BG_GROUPS` in
    /// `tools/gen_act_placeholders.py` -- the generator writes the scenes and
    /// this list reads them, and `TeyvatFrameTests` pins the two equal.
    /// </summary>
    internal static readonly string[] LayerSlots =
    {
        "Layer_00", "Layer_01", "Layer_02", "Layer_03", "Layer_04", "Foreground",
    };

    private static NCombatBackgroundFactory? _instance;

    /// <summary>
    /// Construct it once. `NodeFactory&lt;T&gt;`'s constructor registers the
    /// instance into BaseLib's static factory table, so building a second one
    /// would silently replace the first; the guard makes the call idempotent
    /// for a caller that cannot know whether it has run.
    /// </summary>
    internal static void Ensure() => _instance ??= new NCombatBackgroundFactory();

    private NCombatBackgroundFactory() : base(Slots())
    {
    }

    private static IEnumerable<INodeInfo> Slots()
    {
        foreach (var name in LayerSlots)
        {
            yield return new NodeInfo<Control>(name, false);
        }
    }

    /// <summary>
    /// A slot the scene did not carry. `NCombatBackground` only ever calls
    /// `AddChildSafely` on these, so an empty `Control` at the right name is
    /// the whole requirement -- and a background short one layer node then
    /// draws one layer fewer rather than throwing.
    /// </summary>
    protected override void GenerateNode(Node target, INodeInfo required)
    {
        var slot = new Control { Name = required.Path };
        target.AddChild(slot);
        slot.Owner = target;
    }
}
