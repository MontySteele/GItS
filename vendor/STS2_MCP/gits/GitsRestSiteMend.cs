// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// CO-OP REST SITE: MEND MUST LAND ON THE PARTNER AND SPEND THE REST ACTION.
//
// THE DEFECT (`review/records/coop-paired-round-2026-10-09.md`, about 10
// seats on 3 seeds). `choose_rest_option` on Mend answered "ok", yet Smith or
// Rest was still accepted afterwards, and the heal mostly did not show.
//
// THE CAUSE, read off the v0.111.0 decompile. `MendRestSiteOption.OnSelect`
// does not heal on the click. For the local player it calls
// `NTargetManager.StartTargeting(TargetType.AnyPlayer, ...)` and awaits
// `SelectionFinished()`, a mouse or controller pick of the partner. The bridge
// only ForceClicked the button, so nothing ever made that pick. The next
// command (Smith opens a card-select overlay) tripped Mend's
// `ShouldCancelTargeting`, the targeting finished with no node, `OnSelect`
// returned false, and `RestSiteSynchronizer.ChooseOption` kept every option,
// so the rest action was never spent. A heal showed only when a stray hover
// happened to sit on the partner.
//
// THE FIX. Name the partner before the click (the living rest-site character
// that is not the local player, which is exactly the set Mend's own
// `AllowHoveringNode` and the game's controller path offer), then, once the
// click has opened the targeting, hover that character and finish the pick.
// `OnSelect` then heals the partner and returns true, and the synchronizer
// removes the option or clears the rest, exactly as it does for Rest and
// Smith. `FinishTargeting` is private, so it is reached by reflection; a game
// update that renames it fails here, loudly, rather than silently returning to
// the old defect.
//
// Pinned by tier0/tests/test_coop_rest_site_mend.py.

using System.Linq;
using System.Reflection;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.RestSite;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.RestSite;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace STS2_MCP;

public static class GitsRestSiteMend
{
    /// <summary>True for the option that needs a partner picked after its click.</summary>
    public static bool IsMend(RestSiteOption option) => option is MendRestSiteOption;

    /// <summary>The partner Mend will heal: the first living rest-site
    /// character that is not the local player, or null when there is none.</summary>
    public static NRestSiteCharacter? Partner(NRestSiteRoom room) =>
        room.characterAnims.FirstOrDefault(c =>
            c.Player != null
            && !LocalContext.IsMe(c.Player)
            && !c.Player.Creature.IsDead);

    private static readonly MethodInfo? FinishTargeting =
        typeof(NTargetManager).GetMethod("FinishTargeting",
            BindingFlags.Instance | BindingFlags.NonPublic);

    /// <summary>Complete the targeting Mend's click opened, on the partner.
    /// Returns null on success, or why it could not.</summary>
    public static string? AimAt(NRestSiteCharacter partner)
    {
        var targetManager = NTargetManager.Instance;
        if (targetManager == null || !targetManager.IsInSelection)
            return "Mend did not open its partner pick";
        if (FinishTargeting == null)
            return "NTargetManager.FinishTargeting not found (game update?)";
        if (!targetManager.AllowedToTargetNode(partner))
        {
            targetManager.CancelTargeting();
            return "the partner could not be targeted";
        }
        targetManager.OnNodeHovered(partner);
        FinishTargeting.Invoke(targetManager, new object[] { false });
        return null;
    }
}
