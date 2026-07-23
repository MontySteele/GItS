namespace KleeMod.Elements;

/// <summary>
/// The six Teyvat elements the reaction system understands.
/// </summary>
public enum Element
{
    None = 0,
    Pyro,
    Hydro,
    Electro,
    Cryo,
    Anemo,
    Geo,
}

/// <summary>
/// Carried by any card that deals element-tagged damage.
///
/// WHY THIS EXISTS (spike S1 finding, ruled 2026-07-19): damage events do NOT
/// carry an element. <c>ValueProp</c> is a fixed engine flags enum with no free
/// bits for mods, and <c>ModifyDamageMultiplicative</c> receives no
/// mod-extensible context object. So the element has to travel out-of-band, and
/// the ruling was to hang it on the card.
///
/// Precedent for reaching sideways to <c>cardSource</c> like this is
/// first-party: VulnerablePower inspects the dealer for PaperPhrog and
/// CrueltyPower, and Downfall's GoopPower tests
/// <c>cardSource is IDoubleGoopBonus</c>.
///
/// KNOWN CONSEQUENCE: element is a property of the CARD, not of the damage
/// instance. Damage with no card source -- bomb detonations, Electro-Charged
/// DoT ticks -- cannot be tagged this way and needs its own answer when those
/// systems land in C2.2. See DECISIONS.md.
/// </summary>
public interface IElementalCard
{
    Element Element { get; }
}

/// <summary>
/// Elements that leave a lingering aura. Anemo and Geo never do -- they only
/// trigger off an existing aura (design principles section 2.1, and
/// AURA_ELEMENTS in tier0/engine/reactions.py).
/// </summary>
public static class ElementRules
{
    public static bool LeavesAura(this Element element) =>
        element is Element.Pyro or Element.Hydro or Element.Electro or Element.Cryo;
}
