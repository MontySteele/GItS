using System;
using System.Collections.Generic;
using System.Linq;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.HoverTips;
// GItS LOCAL EDIT (`EB-607`): the two namespaces the game's own
// `AttackIntent.GetSingleDamage` folds a number through.
using MegaCrit.Sts2.Core.Hooks;
using MegaCrit.Sts2.Core.ValueProps;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.MonsterMoves.Intents;
using MegaCrit.Sts2.Core.MonsterMoves.MonsterMoveStateMachine;
using MegaCrit.Sts2.Core.Entities.Merchant;
using MegaCrit.Sts2.Core.Entities.RestSite;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Models.Events;
using MegaCrit.Sts2.Core.Nodes.Events;
using MegaCrit.Sts2.Core.Nodes.Events.Custom;
using MegaCrit.Sts2.Core.Nodes.Events.Custom.CrystalSphere;
using MegaCrit.Sts2.Core.Nodes.GodotExtensions;
using MegaCrit.Sts2.Core.Map;
using MegaCrit.Sts2.Core.Nodes.Cards;
using MegaCrit.Sts2.Core.Nodes.Cards.Holders;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.Nodes.Rewards;
using MegaCrit.Sts2.Core.Nodes.Screens;
using MegaCrit.Sts2.Core.Nodes.Screens.CardSelection;
using MegaCrit.Sts2.Core.Nodes.Screens.Map;
using MegaCrit.Sts2.Core.Nodes.Relics;
using MegaCrit.Sts2.Core.Nodes.Screens.Overlays;
using MegaCrit.Sts2.Core.Nodes.Screens.Shops;
using MegaCrit.Sts2.Core.Nodes.Screens.TreasureRoomRelic;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Models.Monsters;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Models.RelicPools;
using MegaCrit.Sts2.Core.Nodes.Screens.CharacterSelect;
using MegaCrit.Sts2.Core.Nodes.Screens.MainMenu;
using MegaCrit.Sts2.Core.Multiplayer;
using MegaCrit.Sts2.Core.Multiplayer.Game;
using MegaCrit.Sts2.Core.Multiplayer.Game.Lobby;
using MegaCrit.Sts2.Core.Entities.Multiplayer;
using MegaCrit.Sts2.Core.Platform;
using MegaCrit.Sts2.Core.Platform.Steam;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Nodes.Screens.GameOverScreen;
using MegaCrit.Sts2.Core.Nodes.Screens.Timeline;
using MegaCrit.Sts2.Core.Nodes.Screens.Settings;
using MegaCrit.Sts2.Core.Nodes.Screens.ProfileScreen;
using Godot;

namespace STS2_MCP;

public static partial class McpMod
{
    private static Dictionary<string, object?> BuildGameState()
    {
        var result = new Dictionary<string, object?>();
        var tree = (Godot.Engine.GetMainLoop()) as SceneTree;

        if (tree?.Root != null)
        {
            var ftueState = BuildVisibleFtueState(tree.Root);
            if (ftueState != null)
                return ftueState;
        }

        if (!RunManager.Instance.IsInProgress)
        {
            result["state_type"] = "menu";

            // Detect which menu screen is active
            if (tree?.Root != null)
            {
                if (!result.ContainsKey("menu_screen"))
                {
                // Check for singleplayer submenu (Standard / Daily / Custom)
                var spSubmenu = FindFirst<NSingleplayerSubmenu>(tree.Root);
                if (spSubmenu != null && IsNodeVisible(spSubmenu))
                {
                    result["menu_screen"] = "singleplayer";
                    result["message"] = "Select game mode.";

                    var modeOptions = new List<Dictionary<string, object?>>();
                    var modeFields = new[] { ("_standardButton", "standard"), ("_dailyButton", "daily"), ("_customButton", "custom") };
                    foreach (var (fieldName, label) in modeFields)
                    {
                        try
                        {
                            var btn = GetInstanceFieldValue(spSubmenu, fieldName);
                            if (btn is Control ctrl && IsNodeVisible(ctrl))
                            {
                                var isEnabled = btn.GetType().GetProperty("IsEnabled")?.GetValue(btn) as bool?;
                                modeOptions.Add(new Dictionary<string, object?>
                                {
                                    ["name"] = label,
                                    ["enabled"] = isEnabled ?? true
                                });
                            }
                        }
                        catch { }
                    }
                    AddMenuOptionIfVisible(modeOptions, spSubmenu, "_backButton", "back");
                    result["options"] = modeOptions;
                }
                // Check for multiplayer host submenu (Standard / Daily / Custom for multiplayer)
                else
                {
                    var mpHostSubmenu = FindFirst<NMultiplayerHostSubmenu>(tree.Root);
                    if (mpHostSubmenu != null && IsNodeVisible(mpHostSubmenu))
                    {
                        result["menu_screen"] = "multiplayer_host";
                        result["message"] = "Multiplayer host: select game mode.";

                        var modeOptions = new List<Dictionary<string, object?>>();
                        var modeFields = new[] { ("_standardButton", "standard"), ("_dailyButton", "daily"), ("_customButton", "custom") };
                        foreach (var (fieldName, label) in modeFields)
                        {
                            try
                            {
                                var btn = GetInstanceFieldValue(mpHostSubmenu, fieldName);
                                if (btn is Control ctrl && IsNodeVisible(ctrl))
                                {
                                    var isEnabled = btn.GetType().GetProperty("IsEnabled")?.GetValue(btn) as bool?;
                                    modeOptions.Add(new Dictionary<string, object?>
                                    {
                                        ["name"] = label,
                                        ["enabled"] = isEnabled ?? true
                                    });
                                }
                            }
                            catch { }
                        }
                        AddMenuOptionIfVisible(modeOptions, mpHostSubmenu, "_backButton", "back");
                        result["options"] = modeOptions;
                    }
                    else
                    {
                        // Check for multiplayer submenu (Host / Join / Load / Abandon)
                        var mpSubmenu = FindFirst<NMultiplayerSubmenu>(tree.Root);
                        if (mpSubmenu != null && IsNodeVisible(mpSubmenu))
                        {
                            result["menu_screen"] = "multiplayer";
                            result["message"] = "Multiplayer menu.";

                            var mpOptions = new List<Dictionary<string, object?>>();
                            var mpFields = new[] { ("_hostButton", "host"), ("_joinButton", "join"), ("_loadButton", "load"), ("_abandonButton", "abandon") };
                            foreach (var (fieldName, label) in mpFields)
                            {
                                try
                                {
                                    var btn = GetInstanceFieldValue(mpSubmenu, fieldName);
                                    if (btn is Control ctrl && IsNodeVisible(ctrl))
                                    {
                                        var isEnabled = btn.GetType().GetProperty("IsEnabled")?.GetValue(btn) as bool?;
                                        mpOptions.Add(new Dictionary<string, object?>
                                        {
                                            ["name"] = label,
                                            ["enabled"] = isEnabled ?? true
                                        });
                                    }
                                }
                                catch { }
                            }
                            AddMenuOptionIfVisible(mpOptions, mpSubmenu, "_backButton", "back");
                            result["options"] = mpOptions;
                        }
                    }
                }
                // Multiplayer Join Friend screen (lives in the same submenu stack as
                // NMultiplayerSubmenu; pushed when the user clicks "join")
                if (result.ContainsKey("menu_screen") == false)
                {
                    var joinScreen = FindFirst<NJoinFriendScreen>(tree.Root);
                    if (joinScreen != null && IsNodeVisible(joinScreen))
                    {
                        AddMultiplayerJoinMenuState(result, joinScreen);
                    }
                }

                // Multiplayer Load lobby — resume saved MP run. Pushed by NMultiplayerSubmenu
                // when "load" is clicked (host) or by JoinFlow when joining a save in progress (client).
                if (result.ContainsKey("menu_screen") == false)
                {
                    var loadLobby = FindFirst<NMultiplayerLoadGameScreen>(tree.Root);
                    if (loadLobby != null && IsNodeVisible(loadLobby))
                    {
                        AddMultiplayerLoadLobbyMenuState(result, loadLobby);
                    }
                }

                // Check for character select screen
                if (result.ContainsKey("menu_screen") == false)
                {
                    var charSelect = FindFirst<NCharacterSelectScreen>(tree.Root);
                    if (charSelect != null && IsNodeVisible(charSelect))
                    {
                        AddCharacterSelectMenuState(result, charSelect);
                    }
                    else
                    {
                        // Check for other screens
                        var timelineScreen = FindFirst<NTimelineScreen>(tree.Root);
                        var compendiumSubmenu = FindFirst<NCompendiumSubmenu>(tree.Root);
                        var settingsScreen = FindFirst<NSettingsScreen>(tree.Root);

                        if (timelineScreen != null && IsNodeVisible(timelineScreen))
                        {
                            result["menu_screen"] = "timeline";
                            result["message"] = "Timeline screen.";
                            result["options"] = new List<Dictionary<string, object?>>
                            {
                                new() { ["name"] = "advance", ["enabled"] = true },
                                new() { ["name"] = "back", ["enabled"] = true }
                            };

                            // Read epochs from ProgressState (stable, not hover-dependent)
                            try
                            {
                                var progress = SaveManager.Instance?.Progress;
                                if (progress != null)
                                {
                                    var epochList = new List<Dictionary<string, object?>>();
                                    var revealedCount = 0;
                                    var obtainedCount = 0;
                                    var lockedCount = 0;
                                    var noSlotCount = 0;
                                    foreach (var epoch in progress.Epochs)
                                    {
                                        var eraName = epoch.Id;
                                        var state = epoch.State.ToString();
                                        // Clean up ID to readable name
                                        var name = System.Text.RegularExpressions.Regex.Replace(eraName, @"(\d+)$", "");
                                        name = System.Text.RegularExpressions.Regex.Replace(name, @"(?<=[a-z])(?=[A-Z])", " ");

                                        switch (epoch.State)
                                        {
                                            case EpochState.Revealed:
                                                revealedCount++;
                                                break;
                                            case EpochState.Obtained:
                                            case EpochState.ObtainedNoSlot:
                                                obtainedCount++;
                                                break;
                                            case EpochState.NotObtained:
                                                lockedCount++;
                                                break;
                                            case EpochState.NoSlot:
                                                noSlotCount++;
                                                break;
                                        }

                                        epochList.Add(new Dictionary<string, object?>
                                        {
                                            ["id"] = eraName,
                                            ["name"] = name,
                                            ["state"] = state,
                                            ["obtained"] = epoch.ObtainDate
                                        });
                                    }

                                    result["epochs"] = epochList;
                                    result["total_slots"] = epochList.Count;
                                    result["completed_count"] = revealedCount;
                                    result["revealed_count"] = revealedCount;
                                    result["obtained_unrevealed_count"] = obtainedCount;
                                    result["locked_count"] = lockedCount;
                                    result["no_slot_count"] = noSlotCount;
                                }
                            }
                            catch { }
                        }
                        else if (compendiumSubmenu != null && IsNodeVisible(compendiumSubmenu))
                        {
                            result["menu_screen"] = "compendium";
                            result["message"] = "Compendium screen.";
                        }
                        else if (settingsScreen != null && IsNodeVisible(settingsScreen))
                        {
                            result["menu_screen"] = "settings";
                            result["message"] = "Settings screen.";
                        }
                        else
                        {
                            var profileScreen = FindFirst<NProfileScreen>(tree.Root);
                            if (profileScreen != null && IsNodeVisible(profileScreen))
                            {
                                result["menu_screen"] = "profile_select";
                                result["message"] = "Profile select screen.";
                                result["current_profile_id"] = SaveManager.Instance?.CurrentProfileId;

                                var options = new List<Dictionary<string, object?>>();
                                var buttons = GetInstanceFieldValue(profileScreen, "_profileButtons") as System.Collections.IEnumerable;
                                if (buttons != null)
                                {
                                    foreach (var btn in buttons)
                                    {
                                        var btnId = GetInstanceFieldValue(btn, "_profileId");
                                        if (btnId is int id)
                                        {
                                            var enabled = btn.GetType().GetProperty("IsEnabled")?.GetValue(btn) as bool?;
                                            options.Add(new Dictionary<string, object?>
                                            {
                                                ["name"] = $"profile_{id}",
                                                ["enabled"] = enabled ?? true
                                            });
                                        }
                                    }
                                }

                                var backBtn = GetInstanceFieldValue(profileScreen, "_backButton")
                                    ?? FindFirst<NBackButton>(profileScreen);
                                if (backBtn is NClickableControl backClickable && IsNodeVisible(backClickable))
                                {
                                    options.Add(new Dictionary<string, object?>
                                    {
                                        ["name"] = "back",
                                        ["enabled"] = backClickable.IsEnabled
                                    });
                                }

                                if (options.Count > 0)
                                    result["options"] = options;
                            }
                        }
                        if (!result.ContainsKey("menu_screen"))
                        {
                            result["menu_screen"] = "main";
                            result["message"] = "Main menu.";

                        var mainMenu = FindFirst<NMainMenu>(tree.Root);
                        if (mainMenu != null)
                        {
                            var options = new List<string>();
                            var blockedOptions = new List<Dictionary<string, object?>>();
                            var fields = new[] { "_continueButton", "_abandonRunButton", "_singleplayerButton", "_multiplayerButton", "_compendiumButton", "_timelineButton", "_settingsButton", "_quitButton" };
                            var labels = new[] { "continue", "abandon_run", "singleplayer", "multiplayer", "compendium", "timeline", "settings", "quit" };
                            var unrevealedEpochs = GetProgressEpochIdsByState("Obtained", "ObtainedNoSlot");
                            for (int i = 0; i < fields.Length; i++)
                            {
                                try
                                {
                                    var btn = GetInstanceFieldValue(mainMenu, fields[i]);
                                    if (btn is NClickableControl clickable &&
                                        clickable.IsEnabled &&
                                        clickable.Visible &&
                                        clickable.IsVisibleInTree())
                                    {
                                        if (labels[i] == "timeline" && unrevealedEpochs.Count > 0)
                                        {
                                            blockedOptions.Add(new Dictionary<string, object?>
                                            {
                                                ["name"] = "timeline",
                                                ["enabled"] = false,
                                                ["reason"] = "manual_epoch_reveal_required",
                                                ["pending_epoch_ids"] = unrevealedEpochs
                                            });
                                            continue;
                                        }

                                        options.Add(labels[i]);
                                    }
                                }
                                catch { }
                            }
                            if (options.Count > 0)
                                result["options"] = options;
                            if (blockedOptions.Count > 0)
                                result["blocked_options"] = blockedOptions;
                        }
                        }
                    }
                }
            }
            } // close if (!result.ContainsKey("menu_screen"))
            else
            {
                result["message"] = "No run in progress.";
            }

            return result;
        }

        var runState = RunManager.Instance.DebugOnlyGetState();
        if (runState == null)
        {
            if (tree?.Root != null)
            {
                var activeCharSelect = FindFirst<NCharacterSelectScreen>(tree.Root);
                if (activeCharSelect != null && IsNodeVisible(activeCharSelect))
                {
                    AddCharacterSelectMenuState(result, activeCharSelect);
                    return result;
                }
            }

            result["state_type"] = "unknown";
            return result;
        }

        // Overlays can appear on top of any room (events, rest sites, combat).
        // Rewards/card-reward overlays defer to the map - they may linger on the
        // overlay stack while the map opens after the player clicks proceed.
        var topOverlay = NOverlayStack.Instance?.Peek();
        var currentRoom = runState.CurrentRoom;
        bool mapIsOpen = IsMapScreenOpenOrVisible();
        if (topOverlay is NCardGridSelectionScreen cardSelectScreen)
        {
            result["state_type"] = "card_select";
            result["card_select"] = BuildCardSelectState(cardSelectScreen, runState);
        }
        else if (topOverlay is NChooseACardSelectionScreen chooseCardScreen)
        {
            result["state_type"] = "card_select";
            result["card_select"] = BuildChooseCardState(chooseCardScreen, runState);
        }
        else if (topOverlay is NChooseABundleSelectionScreen bundleScreen)
        {
            result["state_type"] = "bundle_select";
            result["bundle_select"] = BuildBundleSelectState(bundleScreen, runState);
        }
        else if (topOverlay is NChooseARelicSelection relicSelectScreen)
        {
            result["state_type"] = "relic_select";
            result["relic_select"] = BuildRelicSelectState(relicSelectScreen, runState);
        }
        else if (!mapIsOpen && topOverlay is NCrystalSphereScreen crystalSphereScreen)
        {
            // Mirror the NRewardsScreen guard below: the Crystal Sphere overlay
            // lingers on the stack after proceed is clicked (only ClearScreens
            // on the next room transition pops it). Once the map opens on top,
            // report "map" so state matches the screen the player can interact
            // with. See issue #73.
            result["state_type"] = "crystal_sphere";
            result["crystal_sphere"] = BuildCrystalSphereState(crystalSphereScreen, runState);
        }
        else if (!mapIsOpen && topOverlay is NCardRewardSelectionScreen cardRewardScreen)
        {
            result["state_type"] = "card_reward";
            result["card_reward"] = BuildCardRewardState(cardRewardScreen);
        }
        else if (!mapIsOpen && topOverlay is NRewardsScreen rewardsScreen)
        {
            result["state_type"] = "rewards";
            result["rewards"] = BuildRewardsState(rewardsScreen, runState);
        }
        else if (topOverlay is NGameOverScreen gameOverScreen)
        {
            result["state_type"] = "game_over";
            result["game_over"] = new Dictionary<string, object?>
            {
                ["message"] = "Run ended.",
                ["options"] = new List<string> { "main_menu" }
            };
        }
        else if (topOverlay is IOverlayScreen
                 && topOverlay is not NRewardsScreen
                 && topOverlay is not NCardRewardSelectionScreen
                 && topOverlay is not NCrystalSphereScreen)
        {
            // Catch-all for unhandled overlays - prevents soft-locks.
            // Overlays that linger on the stack while the map takes over
            // (rewards, card reward, Crystal Sphere) are excluded so the
            // fallback below reports "map" once mapIsOpen is true.
            result["state_type"] = "overlay";
            result["overlay"] = new Dictionary<string, object?>
            {
                ["screen_type"] = topOverlay.GetType().Name,
                ["message"] = $"An overlay ({topOverlay.GetType().Name}) is active. It may require manual interaction in-game."
            };
        }
        else if (mapIsOpen)
        {
            result["state_type"] = "map";
            result["map"] = BuildMapState(runState);
        }
        else if (currentRoom is CombatRoom combatRoom)
        {
            if (CombatManager.Instance.IsInProgress)
            {
                // Check for in-combat hand card selection (e.g., "Select a card to exhaust")
                var playerHand = NPlayerHand.Instance;
                if (playerHand != null && playerHand.IsInCardSelection)
                {
                    result["state_type"] = "hand_select";
                    result["hand_select"] = BuildHandSelectState(playerHand, runState);
                    result["battle"] = BuildBattleState(runState, combatRoom);
                }
                else
                {
                    result["state_type"] = combatRoom.RoomType.ToString().ToLower(); // monster, elite, boss
                    result["battle"] = BuildBattleState(runState, combatRoom);
                }
            }
            else
            {
                // After combat ends - reward/card overlays are caught by top-level checks above.
                // Only handle map and the brief transition before rewards appear.
                if (IsMapScreenOpenOrVisible())
                {
                    result["state_type"] = "map";
                    result["map"] = BuildMapState(runState);
                }
                else
                {
                    result["state_type"] = combatRoom.RoomType.ToString().ToLower();
                    result["message"] = "Combat ended. Waiting for rewards...";
                }
            }
        }
        else if (currentRoom is EventRoom eventRoom)
        {
            if (IsMapScreenOpenOrVisible())
            {
                result["state_type"] = "map";
                result["map"] = BuildMapState(runState);
            }
            else if (eventRoom.CanonicalEvent is FakeMerchant)
            {
                result["state_type"] = "fake_merchant";
                result["fake_merchant"] = BuildFakeMerchantState(eventRoom, runState);
            }
            else
            {
                result["state_type"] = "event";
                result["event"] = BuildEventState(eventRoom, runState);
            }
        }
        else if (currentRoom is MapRoom)
        {
            result["state_type"] = "map";
            result["map"] = BuildMapState(runState);
        }
        else if (currentRoom is MerchantRoom merchantRoom)
        {
            if (IsMapScreenOpenOrVisible())
            {
                result["state_type"] = "map";
                result["map"] = BuildMapState(runState);
            }
            else
            {
                // Auto-open the shopkeeper's inventory if not already open.
                // NMerchantRoom.Inventory (UI node) can be null before the scene is fully ready;
                // OpenInventory() itself accesses Inventory.IsOpen, so guard against null.
                var merchUI = NMerchantRoom.Instance;
                if (merchUI?.Inventory != null && !merchUI.Inventory.IsOpen)
                {
                    merchUI.OpenInventory();
                }
                result["state_type"] = "shop";
                result["shop"] = BuildShopState(merchantRoom, runState);
            }
        }
        else if (currentRoom is RestSiteRoom restSiteRoom)
        {
            if (IsMapScreenOpenOrVisible())
            {
                result["state_type"] = "map";
                result["map"] = BuildMapState(runState);
            }
            else
            {
                result["state_type"] = "rest_site";
                result["rest_site"] = BuildRestSiteState(restSiteRoom, runState);
            }
        }
        else if (currentRoom is TreasureRoom treasureRoom)
        {
            if (IsMapScreenOpenOrVisible())
            {
                result["state_type"] = "map";
                result["map"] = BuildMapState(runState);
            }
            else
            {
                result["state_type"] = "treasure";
                result["treasure"] = BuildTreasureState(treasureRoom, runState);
            }
        }
        else if (currentRoom == null && tree?.Root != null)
        {
            var activeCharSelect = FindFirst<NCharacterSelectScreen>(tree.Root);
            if (activeCharSelect != null && IsNodeVisible(activeCharSelect))
            {
                AddCharacterSelectMenuState(result, activeCharSelect);
            }
            else
            {
                result["state_type"] = "unknown";
                result["room_type"] = currentRoom?.GetType().Name;
            }
        }
        else
        {
            result["state_type"] = "unknown";
            result["room_type"] = currentRoom?.GetType().Name;
        }

        // Common run info
        result["run"] = new Dictionary<string, object?>
        {
            ["act"] = runState.CurrentActIndex + 1,
            ["floor"] = runState.TotalFloor,
            ["ascension"] = runState.AscensionLevel
        };

        // Always include full player data (relics, potions, deck, etc.) on every screen
        var _player = LocalContext.GetMe(runState);
        if (_player != null)
        {
            result["player"] = BuildPlayerState(_player);
        }

        return result;
    }

    private static void AddCharacterSelectMenuState(
        Dictionary<string, object?> result,
        NCharacterSelectScreen charSelect)
    {
        result["state_type"] = "menu";
        result["menu_screen"] = "character_select";
        result["message"] = "Select a character.";

        var buttons = FindAll<NCharacterSelectButton>(charSelect);
        var characters = new List<Dictionary<string, object?>>();
        var options = new List<Dictionary<string, object?>>();
        foreach (var btn in buttons)
        {
            try
            {
                if (btn.Character is { } cm && IsNodeVisible(btn))
                {
                    var characterId = cm.Id.Entry;
                    var characterName = SafeGetText(() => cm.Title);
                    options.Add(new Dictionary<string, object?>
                    {
                        ["name"] = characterId,
                        ["enabled"] = !btn.IsLocked
                    });

                    var charData = new Dictionary<string, object?>
                    {
                        ["name"] = characterName,
                        ["id"] = characterId,
                        ["locked"] = btn.IsLocked,
                        ["hp"] = cm.StartingHp,
                        ["gold"] = cm.StartingGold,
                        ["energy"] = cm.MaxEnergy,
                        ["description"] = SafeGetText(() => cm.CardsModifierDescription),
                    };

                    var startRelics = new List<Dictionary<string, object?>>();
                    foreach (var relic in cm.StartingRelics)
                    {
                        startRelics.Add(new Dictionary<string, object?>
                        {
                            ["name"] = SafeGetText(() => relic.Title),
                            ["description"] = SafeGetText(() => relic.DynamicDescription)
                        });
                    }
                    if (startRelics.Count > 0)
                        charData["starting_relics"] = startRelics;

                    var deckCards = new List<string>();
                    foreach (var card in cm.StartingDeck)
                        deckCards.Add(SafeGetText(() => card.Title) ?? "?");
                    if (deckCards.Count > 0)
                        charData["starting_deck"] = deckCards;

                    try
                    {
                        var allCards = cm.CardPool?.AllCards;
                        if (allCards != null)
                            charData["total_cards"] = System.Linq.Enumerable.Count(allCards);
                    }
                    catch { }

                    try
                    {
                        var allRelics = cm.RelicPool?.AllRelics;
                        if (allRelics != null)
                            charData["total_relics"] = System.Linq.Enumerable.Count(allRelics);
                    }
                    catch { }

                    try
                    {
                        var allPotions = cm.PotionPool?.AllPotions;
                        if (allPotions != null)
                            charData["total_potions"] = System.Linq.Enumerable.Count(allPotions);
                    }
                    catch { }

                    characters.Add(charData);
                }
            }
            catch { }
        }
        if (characters.Count > 0)
            result["characters"] = characters;

        var embarkBtn = GetInstanceFieldValue(charSelect, "_embarkButton");
        if (embarkBtn is NClickableControl embarkClickable && IsNodeVisible(embarkClickable))
        {
            options.Add(new Dictionary<string, object?>
            {
                ["name"] = "confirm",
                ["enabled"] = embarkClickable.IsEnabled
            });
            options.Add(new Dictionary<string, object?>
            {
                ["name"] = "embark",
                ["enabled"] = embarkClickable.IsEnabled
            });
        }

        // _backButton and _unreadyButton are surfaced as distinct options so MP callers
        // can distinguish "leave the lobby" from "retract my ready vote". In SP, only
        // _backButton ever becomes enabled. See NCharacterSelectScreen.OnEmbarkPressed /
        // OnUnreadyPressed for the toggle logic.
        var backBtn = GetInstanceFieldValue(charSelect, "_backButton");
        if (backBtn is NClickableControl backClickable && IsNodeVisible(backClickable))
        {
            options.Add(new Dictionary<string, object?>
            {
                ["name"] = "back",
                ["enabled"] = backClickable.IsEnabled
            });
        }

        // MP lobby block — surfaces roster / ready state / ascension when this character
        // select is part of a host or client lobby. SP runs leave the field absent.
        bool isMpCharSelect = false;
        try
        {
            var lobby = charSelect.Lobby;
            if (lobby != null && lobby.NetService != null && lobby.NetService.Type.IsMultiplayer())
            {
                isMpCharSelect = true;
                result["lobby"] = BuildStartRunLobbyState(lobby);
            }
        }
        catch { }

        // _unreadyButton is part of the scene in SP too but never becomes enabled there.
        // Only surface it as an option in MP, where it has a real role.
        if (isMpCharSelect)
        {
            var unreadyBtn = GetInstanceFieldValue(charSelect, "_unreadyButton");
            if (unreadyBtn is NClickableControl unreadyClickable && IsNodeVisible(unreadyClickable))
            {
                options.Add(new Dictionary<string, object?>
                {
                    ["name"] = "unready",
                    ["enabled"] = unreadyClickable.IsEnabled
                });
            }
        }

        if (options.Count > 0)
            result["options"] = options;
    }

    private static Dictionary<string, object?> BuildStartRunLobbyState(StartRunLobby lobby)
    {
        var lobbyState = new Dictionary<string, object?>
        {
            ["type"] = lobby.NetService.Type switch
            {
                NetGameType.Host => "host",
                NetGameType.Client => "client",
                NetGameType.Singleplayer => "singleplayer",
                _ => lobby.NetService.Type.ToString().ToLowerInvariant()
            },
            ["game_mode"] = lobby.GameMode.ToString().ToLowerInvariant(),
            // GItS LOCAL EDIT (EB-171, game v0.111.0). `StartRunLobby.MaxPlayers`
            // was removed; the value survives only as the private readonly
            // `_maxPlayers` the constructor stores and `AddPlayer` /
            // `SetLocalCharacter` compare `Players.Count` against. There is no
            // public replacement and no other member carries the number -- the
            // lobby's own UI reads the private field too -- so this is a
            // reflection read with a null fallback rather than a guess. The key
            // stays in the payload either way: a MISSING value now means "the
            // game stopped exposing it", not "singleplayer".
            ["max_players"] = StartRunLobbyMaxPlayers(lobby),
            ["ascension"] = lobby.Ascension,
            ["max_ascension"] = lobby.MaxAscension,
            ["all_ready"] = lobby.Players.Count > 0 && lobby.Players.All(p => p.isReady),
            ["is_about_to_begin"] = SafeIsAboutToBeginGame(lobby)
        };

        // is_local_ready === local player has hit Embark in MP and is now waiting.
        // Mirrors NCharacterSelectScreen._readyAndWaitingContainer.Visible.
        try
        {
            var local = lobby.LocalPlayer;
            lobbyState["is_local_ready"] = local.isReady;
            lobbyState["local_player_id"] = local.id.ToString();
        }
        catch { }

        var players = new List<Dictionary<string, object?>>();
        ulong localId;
        try { localId = lobby.LocalPlayer.id; } catch { localId = 0; }
        ulong hostId = lobby.NetService.Type == NetGameType.Host ? localId : 0;

        foreach (var p in lobby.Players)
        {
            var entry = new Dictionary<string, object?>
            {
                ["id"] = p.id.ToString(),
                ["slot_id"] = p.slotId,
                ["is_local"] = p.id == localId,
                // We can only positively identify the host as "us" when we ARE the host;
                // a client doesn't know which remote id is the host without inspecting
                // the net service. Keep it simple and only flag is_host=true for self
                // when hosting — clients can infer host-ness by player_id when needed.
                ["is_host"] = p.id == hostId && hostId != 0,
                ["character"] = SafeGetText(() => p.character?.Title)
                                ?? p.character?.Id.Entry,
                ["character_id"] = p.character?.Id.Entry,
                ["is_ready"] = p.isReady,
                ["platform_name"] = SafeGetPlayerName(lobby.NetService.Platform, p.id)
            };
            players.Add(entry);
        }
        lobbyState["players"] = players;
        lobbyState["player_count"] = players.Count;

        if (!string.IsNullOrEmpty(lobby.Seed))
            lobbyState["seed"] = lobby.Seed;

        return lobbyState;
    }

    // GItS LOCAL EDIT (EB-171, game v0.111.0). See the call site in
    // BuildStartRunLobbyState. Returns null rather than 0 or a made-up 2 when
    // the field cannot be read, so a reader can tell "unknown" from "one seat".
    private static int? StartRunLobbyMaxPlayers(StartRunLobby lobby)
    {
        try
        {
            var field = typeof(StartRunLobby).GetField(
                "_maxPlayers",
                System.Reflection.BindingFlags.NonPublic |
                System.Reflection.BindingFlags.Instance);
            return field?.GetValue(lobby) as int?;
        }
        catch { return null; }
    }

    private static bool SafeIsAboutToBeginGame(StartRunLobby lobby)
    {
        try { return lobby.IsAboutToBeginGame(); }
        catch { return false; }
    }

    private static string? SafeGetPlayerName(PlatformType platform, ulong playerId)
    {
        try { return PlatformUtil.GetPlayerName(platform, playerId); }
        catch { return null; }
    }

    private static void AddMultiplayerJoinMenuState(
        Dictionary<string, object?> result,
        NJoinFriendScreen joinScreen)
    {
        result["state_type"] = "menu";
        result["menu_screen"] = "multiplayer_join";

        // FastMP: when Steam isn't initialized OR --fastmp is set, OnSubmenuOpened auto-
        // joins localhost:33771 instead of presenting friends. This is a debug/local-dev
        // path. We surface it so callers don't try to hit "refresh" expecting a list.
        bool fastMp = !SteamInitializer.Initialized || CommandLineHelper.HasArg("fastmp");
        result["fast_mp"] = fastMp;

        var loadingFriends = GetInstanceFieldValue(joinScreen, "_loadingFriendsIndicator") as Control;
        var loadingOverlay = GetInstanceFieldValue(joinScreen, "_loadingOverlay") as Control;
        bool loading = (loadingFriends != null && loadingFriends.Visible)
                       || (loadingOverlay != null && loadingOverlay.Visible);
        result["loading"] = loading;

        var noFriendsLabel = GetInstanceFieldValue(joinScreen, "_noFriendsLabel") as Control;
        bool noFriends = noFriendsLabel != null && noFriendsLabel.Visible;
        result["no_friends"] = noFriends;

        var friends = new List<Dictionary<string, object?>>();
        var options = new List<Dictionary<string, object?>>();

        var buttonContainer = GetInstanceFieldValue(joinScreen, "_buttonContainer") as Control;
        if (buttonContainer != null)
        {
            int index = 0;
            foreach (var child in buttonContainer.GetChildren())
            {
                if (child is NJoinFriendButton friendBtn)
                {
                    string? name = null;
                    try { name = PlatformUtil.GetPlayerName(PlatformUtil.PrimaryPlatform, friendBtn.PlayerId); }
                    catch { }

                    friends.Add(new Dictionary<string, object?>
                    {
                        ["index"] = index,
                        ["name"] = name,
                        ["player_id"] = friendBtn.PlayerId.ToString(),
                        ["enabled"] = friendBtn.IsEnabled
                    });
                    options.Add(new Dictionary<string, object?>
                    {
                        ["name"] = $"join_{index}",
                        ["enabled"] = friendBtn.IsEnabled
                    });
                    index++;
                }
            }
        }
        result["friends"] = friends;

        var refreshBtn = GetInstanceFieldValue(joinScreen, "_refreshButton") as NClickableControl;
        if (refreshBtn != null && IsNodeVisible(refreshBtn))
        {
            options.Add(new Dictionary<string, object?>
            {
                ["name"] = "refresh",
                ["enabled"] = refreshBtn.IsEnabled && !loading
            });
        }
        AddMenuOptionIfVisible(options, joinScreen, "_backButton", "back");

        if (fastMp)
        {
            result["message"] = loading
                ? "FastMP join flow is connecting to localhost:33771..."
                : "FastMP mode (no Steam): join screen auto-connects to localhost:33771.";
        }
        else if (loading)
        {
            result["message"] = "Refreshing friend list...";
        }
        else if (noFriends)
        {
            result["message"] = "No friends with open lobbies. Use 'refresh' to retry, or 'back' to return.";
        }
        else
        {
            result["message"] = "Pick a friend to join, or 'refresh' to update the list.";
        }

        result["options"] = options;
    }

    private static void AddMultiplayerLoadLobbyMenuState(
        Dictionary<string, object?> result,
        NMultiplayerLoadGameScreen loadLobby)
    {
        result["state_type"] = "menu";
        result["menu_screen"] = "multiplayer_load_lobby";

        var lobby = GetInstanceFieldValue(loadLobby, "_runLobby") as LoadRunLobby;
        if (lobby != null)
        {
            var info = new Dictionary<string, object?>
            {
                ["type"] = lobby.NetService.Type switch
                {
                    NetGameType.Host => "host",
                    NetGameType.Client => "client",
                    _ => lobby.NetService.Type.ToString().ToLowerInvariant()
                },
                ["game_mode"] = lobby.GameMode.ToString().ToLowerInvariant(),
                ["ascension"] = lobby.Run?.Ascension ?? 0,
                ["act"] = (lobby.Run?.CurrentActIndex ?? 0) + 1,
                ["floor"] = lobby.Run?.VisitedMapCoords?.Count ?? 0
            };

            try
            {
                var localPlayer = lobby.Run?.Players?.FirstOrDefault(p => p.NetId == lobby.NetService.NetId);
                if (localPlayer != null)
                {
                    info["character_id"] = localPlayer.CharacterId?.Entry;
                    info["current_hp"] = localPlayer.CurrentHp;
                    info["max_hp"] = localPlayer.MaxHp;
                    info["gold"] = localPlayer.Gold;
                }
            }
            catch { }

            info["expected_player_count"] = lobby.Run?.Players?.Count ?? 0;
            // GItS LOCAL EDIT (EB-171, game v0.111.0). `ConnectedPlayerIds` is
            // gone from both lobbies; `LoadRunLobby` now holds a
            // `List<LoadRunLobbyPlayer> Players` whose members are exactly the
            // players connected to the load lobby (they are added by
            // `OnConnectedToClientAsHost` / the join-response handler and
            // removed on disconnect), and exposes `PlayerCount` and
            // `PlayerIds` over it. Those two are the replacement, member for
            // member -- the three reads below take them.
            info["connected_player_count"] = lobby.PlayerCount;

            // LoadRunLobby no longer exposes IsAboutToBeginGame in the public game API,
            // so derive the same readiness summary from connected players and ready flags.
            // Without these fields, FormatLobbyMarkdown printed "All ready: false" unconditionally for load lobbies.
            bool aboutToBegin = false;
            try
            {
                var runPlayers = lobby.Run?.Players;
                var connectedPlayerIds = lobby.PlayerIds?.ToList();   // GItS LOCAL EDIT (EB-171)
                aboutToBegin = runPlayers != null
                    && connectedPlayerIds != null
                    && runPlayers.Count > 0
                    && runPlayers.All(player => connectedPlayerIds.Contains(player.NetId) && lobby.IsPlayerReady(player.NetId));
            }
            catch { }
            info["all_ready"] = aboutToBegin;
            info["is_about_to_begin"] = aboutToBegin;

            // Per-player ready/connected breakdown
            var players = new List<Dictionary<string, object?>>();
            try
            {
                if (lobby.Run?.Players != null)
                {
                    foreach (var sp in lobby.Run.Players)
                    {
                        // GItS LOCAL EDIT (EB-171)
                        bool isConnected = lobby.Players?.Any(p => p.id == sp.NetId) ?? false;
                        bool isReady = false;
                        try { isReady = lobby.IsPlayerReady(sp.NetId); } catch { }
                        players.Add(new Dictionary<string, object?>
                        {
                            ["id"] = sp.NetId.ToString(),
                            ["is_local"] = sp.NetId == lobby.NetService.NetId,
                            ["character_id"] = sp.CharacterId?.Entry,
                            ["is_connected"] = isConnected,
                            ["is_ready"] = isReady,
                            ["platform_name"] = SafeGetPlayerName(lobby.NetService.Platform, sp.NetId)
                        });
                    }
                }
            }
            catch { }
            info["players"] = players;

            result["lobby"] = info;
        }

        var options = new List<Dictionary<string, object?>>();

        var confirmBtn = GetInstanceFieldValue(loadLobby, "_confirmButton") as NClickableControl;
        if (confirmBtn != null && IsNodeVisible(confirmBtn))
        {
            options.Add(new Dictionary<string, object?>
            {
                ["name"] = "confirm",
                ["enabled"] = confirmBtn.IsEnabled
            });
            options.Add(new Dictionary<string, object?>
            {
                ["name"] = "embark",
                ["enabled"] = confirmBtn.IsEnabled
            });
        }

        var backBtn2 = GetInstanceFieldValue(loadLobby, "_backButton") as NClickableControl;
        if (backBtn2 != null && IsNodeVisible(backBtn2))
        {
            options.Add(new Dictionary<string, object?>
            {
                ["name"] = "back",
                ["enabled"] = backBtn2.IsEnabled
            });
        }

        var unreadyBtn2 = GetInstanceFieldValue(loadLobby, "_unreadyButton") as NClickableControl;
        if (unreadyBtn2 != null && IsNodeVisible(unreadyBtn2))
        {
            options.Add(new Dictionary<string, object?>
            {
                ["name"] = "unready",
                ["enabled"] = unreadyBtn2.IsEnabled
            });
        }

        result["options"] = options;
        result["message"] = "Multiplayer load lobby. Confirm to ready up; once everyone is connected and ready, the run resumes.";
    }

    private static Dictionary<string, object?> BuildBattleState(RunState runState, CombatRoom combatRoom)
    {
        var combatState = CombatManager.Instance.DebugOnlyGetState();
        var battle = new Dictionary<string, object?>();

        if (combatState == null)
        {
            battle["error"] = "Combat state unavailable";
            return battle;
        }

        battle["round"] = combatState.RoundNumber;
        battle["turn"] = combatState.CurrentSide.ToString().ToLower();
        battle["is_play_phase"] = IsPlayPhase(combatState);

        // Enemies
        var enemies = new List<Dictionary<string, object?>>();
        var entityCounts = new Dictionary<string, int>();
        foreach (var creature in combatState.Enemies)
        {
            if (creature.IsAlive)
            {
                enemies.Add(BuildEnemyState(creature, entityCounts));
            }
        }
        battle["enemies"] = enemies;

        return battle;
    }

    private static Dictionary<string, object?> BuildPlayerState(Player player)
    {
        var state = new Dictionary<string, object?>();
        var creature = player.Creature;
        var combatState = player.PlayerCombatState;

        state["character"] = SafeGetText(() => player.Character.Title);
        state["hp"] = creature.CurrentHp;
        state["max_hp"] = creature.MaxHp;
        state["block"] = creature.Block;

        // GItS LOCAL EDIT (`EB-676`). WHETHER THE HP LINE ABOVE HAS SETTLED.
        // There is one HP field on this wire and it is written on every
        // screen, so a victory screen reading 25/80 and the next screen
        // reading 16/80 are that field at two moments -- the first taken
        // before the fight's own end-of-turn queue drained into it. This is
        // the flag that tells the two moments apart, so the blind page can
        // print the number plainly when nothing is in flight instead of
        // hedging every figure it draws. Always emitted, so a MISSING key
        // means "bridge predates EB-676" and never "settled". The decision
        // and both of its clauses: gits/GitsSettledHp.cs.
        var settled = GitsSettledHp.Unreadable();
        try
        {
            var executor = RunManager.Instance?.ActionExecutor;
            var combat = CombatManager.Instance;
            settled = GitsSettledHp.Decide(
                actionQueueRunning: executor?.IsRunning ?? false,
                actionInFlight: executor?.CurrentlyRunningAction != null,
                combatStateStands: combat?.CurrentCombatId != null,
                // `IsEnding` AND NOT `IsOverOrEnding` (proofs-8a, PR #573).
                // The latter is `IsEnding || !IsInProgress`, so it latches
                // true for every screen after a fight while `CurrentCombatId`
                // stays non-null until the run leaves the ROOM -- which made
                // `hp_settled` false on 26 of 26 post-combat map, rewards and
                // card-reward reads. gits/GitsSettledHp.cs carries it.
                combatEnding: combat?.IsEnding ?? false);
        }
        catch (Exception)
        {
            // Fail closed: a state read must never throw, and an unreadable
            // game is not a settled one.
            settled = GitsSettledHp.Unreadable();
        }
        state[GitsSettledHp.SettledKey] = settled.Settled;
        if (!settled.Settled)
        {
            state[GitsSettledHp.ReasonKey] = settled.Reason;
        }

        // PlayerCombatState can linger after combat while on map/rest/shop. Energy/MaxEnergy getters
        // run hooks (e.g. Hook.ModifyMaxEnergy) that null-ref without a live combat - only serialize
        // combat fields when a fight is actually in progress.
        if (combatState != null && CombatManager.Instance.IsInProgress)
        {
            state["energy"] = combatState.Energy;
            state["max_energy"] = combatState.MaxEnergy;

            // GItS LOCAL EDIT (Understudy P1.5, spec item 2). This method walks
            // `creature.Powers` for the status strip, so a meter without a badge
            // is invisible on the wire -- Furina's Encore is a BaseLib
            // CustomResource and has been recorded as UNSEEN by every bot fight
            // since animation sprint 2 retired its badge. One line, one key,
            // always emitted while a combat is live so that a MISSING key means
            // "bridge predates P1.5" and an EMPTY map means "nothing registered".
            // Implementation and its reflection contract: gits/GitsResources.cs.
            state["resources"] = GitsResourceSnapshot(combatState);

            // GItS LOCAL EDIT (`EB-181`, the meter half). AN ID AND AN AMOUNT
            // IS THE WHOLE OF THE LINE ABOVE, so a meter reaches the page with
            // no ceiling and the blind render has had to say so on every meter
            // row it prints ("the game's data feed carries this meter's amount
            // only: no maximum"). `resources` keeps its shape exactly -- it is
            // an `{id: amount}` map several readers already parse -- and the
            // fuller row rides beside it, per id, so a reader that wants the
            // ceiling asks for it and every reader that does not is unmoved.
            // Implementation and its opt-in contract: gits/GitsResources.cs.
            state["resource_info"] = GitsResourceInfo(combatState);

            // GItS LOCAL EDIT (EB-181, the Kokomi half). A resource snapshot is
            // an id and an amount, which is the whole of EB-181's second half
            // ("a meter has no maximum"): under the Kurage's memory rule Charge
            // HAS a target -- the front memory's own price -- and the queue
            // behind it is a list of cards no wire key carries. A seat that
            // cannot read the queue cannot play the character. Emitted only
            // when this build HAS the rule, so an absent key means "no memory
            // rule here" and an empty map means "this player is not Kokomi".
            // Implementation and its reflection contract: gits/GitsKurageMemory.cs.
            if (GitsKurageMemorySnapshot(player) is { } kurageMemory)
            {
                state["kurage_memory"] = kurageMemory;
            }

            // Stars (The Regent's resource, conditionally shown)
            if (player.Character.ShouldAlwaysShowStarCounter || combatState.Stars > 0)
            {
                state["stars"] = combatState.Stars;
            }

            // Hand
            var hand = new List<Dictionary<string, object?>>();
            int cardIndex = 0;
            foreach (var card in combatState.Hand.Cards)
            {
                hand.Add(BuildCardState(card, cardIndex));
                cardIndex++;
            }
            state["hand"] = hand;

            // Pile counts
            state["draw_pile_count"] = combatState.DrawPile.Cards.Count;
            state["discard_pile_count"] = combatState.DiscardPile.Cards.Count;
            state["exhaust_pile_count"] = combatState.ExhaustPile.Cards.Count;

            // Pile contents (draw pile sorted by rarity then card ID, matching in-game display)
            var drawCards = combatState.DrawPile.Cards.ToList();
            drawCards.Sort((c1, c2) => c1.Rarity != c2.Rarity
                ? c1.Rarity.CompareTo(c2.Rarity)
                : string.Compare(c1.Id.Entry, c2.Id.Entry, StringComparison.Ordinal));
            state["draw_pile"] = BuildPileCardList(drawCards, PileType.Draw);
            state["discard_pile"] = BuildPileCardList(combatState.DiscardPile.Cards, PileType.Discard);
            state["exhaust_pile"] = BuildPileCardList(combatState.ExhaustPile.Cards, PileType.Exhaust);

            // Orbs
            var orbQueue = combatState.OrbQueue;
            if (orbQueue != null && orbQueue.Capacity > 0)
            {
                var orbs = new List<Dictionary<string, object?>>();
                foreach (var orb in orbQueue.Orbs)
                {
                    // Populate SmartDescription placeholders with Focus-modified values,
                    // mirroring OrbModel.HoverTips getter (OrbModel.cs:92-94)
                    string? description = SafeGetText(() =>
                    {
                        var desc = orb.SmartDescription;
                        desc.Add("energyPrefix", orb.Owner.Character.CardPool.Title);
                        desc.Add("Passive", orb.PassiveVal);
                        desc.Add("Evoke", orb.EvokeVal);
                        return desc;
                    });
                    orbs.Add(new Dictionary<string, object?>
                    {
                        ["id"] = orb.Id.Entry,
                        ["name"] = SafeGetText(() => orb.Title),
                        ["description"] = description,
                        ["passive_val"] = orb.PassiveVal,
                        ["evoke_val"] = orb.EvokeVal,
                        ["keywords"] = BuildHoverTips(orb.HoverTips)
                    });
                }
                state["orbs"] = orbs;
                state["orb_slots"] = orbQueue.Capacity;
                state["orb_empty_slots"] = orbQueue.Capacity - orbQueue.Orbs.Count;
            }

            // Pets (Osty for Necrobinder)
            var pets = BuildPetsState(player);
            if (pets.Count > 0)
            {
                state["pets"] = pets;
            }
        }

        state["gold"] = player.Gold;

        // GItS LOCAL EDIT (`EB-447`). THE MASTER DECK, ON EVERY SCREEN.
        //
        // THE FIND (Klee r13 and r15, Furina r7, Kokomi r11). The blind page's
        // deck list is RECONSTRUCTED: `understudy/blindplay_faces.remember_deck`
        // takes the union of the four combat piles at a fight's first round-one
        // read and carries it to the map, the shop and the Smith, because the
        // wire has no deck on any of those screens. Every guard that memory
        // has was bought with a defect -- "after the Haunted Ship the map
        // listed Dazed x5, which are combat-only status cards"; "the same list
        // dropped Catalytic Converter entirely after I played it as a Power";
        // a generated Companion written into the deck because one fight's
        // union happened to be bigger (`EB-528`). All of them are the same
        // thing: a union of combat piles is not a deck.
        //
        // AND THE DECK IS RIGHT HERE. `Player.Deck` is a `CardPile(PileType
        // .Deck)` -- the run's master list, the one the game's own Deck screen
        // draws -- and it is readable on the map, at a shop, at a rest and at
        // a reward, none of which have a `PlayerCombatState` at all. So this
        // sits OUTSIDE the combat block, with `kokomi_plans` and for its
        // reason: the screens that owe a reader a deck are exactly the screens
        // with no fight on them.
        //
        // `BuildPileCardList`'S SHAPE, unchanged, because the page's deck
        // reader already parses that shape four times over (`draw_pile`,
        // `discard_pile`, `exhaust_pile`, and the hand beside them). An ABSENT
        // key is a bridge older than this row and the page keeps the memory it
        // has always kept; a PRESENT key is the deck, and the memory stands
        // down.
        try
        {
            state["master_deck"] = BuildPileCardList(
                player.Deck.Cards, PileType.Deck);
        }
        catch (Exception)
        {
            // A read that throws is not a deck. Absent, and the page's
            // remembered union answers exactly as it did before.
        }

        // GItS LOCAL EDIT (`EB-349` / `EB-611`). WHAT RESOLVED THIS TURN.
        //
        // The standing fact this closes is printed on the page itself
        // (`understudy/blindplay_notes.AUTO_TURN_NOTE`): "there is no record of
        // a card resolving on the wire at all". Every screen this bridge sends
        // is an after-state, so a relic that plays a turn FOR the player
        // (Vakuu: six openings, five from an empty hand -- Kokomi r4d) leaves
        // nothing behind but a board, and a multi-hit random `Set off` (Klee
        // r23 lane 2) tells a seat WHICH bodies were hit and never the order.
        // One ledger answers both: a row per resolved card, the game's own
        // `CardPlay.IsAutoPlay` on it, and the hits under it in hit order.
        // Same absent/empty/populated contract as the rows above, same
        // reflection seam, same turn window:
        // gits/GitsResolutionLedger.cs.
        if (GitsResolutionState() is { } resolutions)
        {
            state[GitsResolutionsKey] = resolutions;
        }

        // GItS LOCAL EDIT (`EB-216`, the Kokomi draft-6 half). The same gap
        // one rule over from `kurage_memory`: the arm's pending-Plans badge
        // reaches the wire as a COUNT, and what the next morning WILL BE is
        // the list behind it -- which Plans, in what order, and whether
        // Nereid's Ascension has made each of them happen twice. The pet's
        // entity id rides here too, because a Plan is played ON the jellyfish
        // and a seat with no id to aim at cannot write one at all. Emitted
        // only when this build HAS the rule. Implementation and its
        // reflection contract: gits/GitsKokomiPlan.cs.
        //
        // OUTSIDE THE COMBAT BLOCK SINCE `EB-329`, and that is the whole of
        // the row's third ask. `KokomiPlan.Snapshot` reads static per-Player
        // records and touches no `CombatState`, so it answers perfectly well
        // once a fight is over -- and the one morning a seat can never see is
        // the one whose kill ENDED the fight, because the next screen the
        // game shows is the reward screen and the combat block does not run
        // for it. The round-5 act-1 seat banked two Plans for an exactly
        // lethal morning and reported "the next screen was the reward
        // screen": the beat it had spent a turn setting up was the only beat
        // of the run with no receipt. Emitting here costs a dictionary on
        // non-combat screens and hands the page that receipt.
        if (GitsKokomiPlanState(player) is { } kokomiPlans)
        {
            state["kokomi_plans"] = kokomiPlans;
        }

        // GItS LOCAL EDIT (`EB-405`). The same receipt one arm over: a Salon
        // member picks its own body and leaves an element on it, and neither
        // fact survives the switch that decides them. Emitted beside the Plan
        // queue and on the same absent/empty/populated contract.
        if (GitsFurinaSalonState(player) is { } furinaSalon)
        {
            state["furina_salon"] = furinaSalon;
        }

        // GItS LOCAL EDIT (`EB-735`). THE STAGE, and it is the block above one
        // arm over: three performers stand in three SEATS, and the seat is the
        // whole kit -- attacks reach the front one, Spend pays from the front
        // one, Raise lands on the back one. The pets already reach the wire;
        // the ORDER they stand in does not, because `Pets` is in the order the
        // bodies were fielded and a rotation breaks it. Emitted beside the two
        // receipts above and on the same absent/empty/populated contract, with
        // one further state: a populated block with no seats is "the stage is
        // empty", which is the fact a seat about to spend a rider needs and
        // the one an absent key cannot state. Implementation and its
        // reflection contract: gits/GitsFurinaStage.cs.
        if (GitsFurinaStageState(player) is { } furinaStage)
        {
            state["furina_stage"] = furinaStage;
        }

        // GItS LOCAL EDIT (`EB-681`). WHAT REACTED THIS TURN, BY NAME. A
        // reaction is what several kits are ABOUT and the feed carried no
        // trace of one: the aura is consumed, the effect lands, and a reader
        // is left working backwards from a number. Kokomi r27 lane 2
        // reconstructed TWO Electro-Charged procs in one beat from a Poison
        // count that was twice what the keyword prints. Emitted beside the
        // two receipts above and on the same absent/empty/populated
        // contract. Implementation and its reflection contract:
        // gits/GitsReactionLog.cs.
        //
        // BOARD-GLOBAL AND NOT PER-PLAYER, which is the mod's own scoping for
        // every shared reaction fact (red-pen R1): a Reaction is a fact about
        // the board, so both seats of a co-op game are shown the beats both
        // of them watched.
        if (GitsReactionLogState() is { } reactions)
        {
            state["reactions"] = reactions;
        }

        // GItS LOCAL EDIT (`EB-610`). WHERE THIS TURN'S SPARKS CAME FROM.
        // Klee r23 lane 2 watched the bank go 2 to 3 across Kaeya and Rapid
        // Fire on a BARE BOARD, while the only sentence on any screen naming a
        // Spark source says "whenever a Bomb goes off" -- so the meter
        // contradicted the one rule the reader had. This is the NARROW read
        // the page needs and not the ledger route: gains of the SPARK meter on
        // the CURRENT turn, each with the card its row opened on, and the
        // engine's event word is turned into a printed one by
        // `understudy/blindplay_board.spark_sources` before any page sees it.
        // Same absent/empty contract as the rows above. Implementation and its
        // reflection contract: gits/GitsMeterLedger.cs.
        if (GitsSparkSourcesState() is { } sparkSources)
        {
            state["spark_sources"] = sparkSources;
        }

        // GItS LOCAL EDIT (`EB-695`). WHAT A RELIC ANSWERED WITH. The
        // Tamakushi Casket's 2 is named inside a Plan carry-out (the rider
        // clause `EB-453` built) and was named NOWHERE when the debuff card
        // was played from hand -- Kokomi r30 lane 2 "subtracted it from HP on
        // every such play". Same shape, same absent/empty/populated contract,
        // same reflection seam: gits/GitsReactionLog.cs.
        if (GitsRelicAnswerState() is { } relicAnswers)
        {
            state["relic_answers"] = relicAnswers;
        }

        // Powers (status effects)
        state["status"] = BuildPowersState(creature);

        // Relics
        var relics = new List<Dictionary<string, object?>>();
        foreach (var relic in player.Relics)
        {
            relics.Add(new Dictionary<string, object?>
            {
                ["id"] = relic.Id.Entry,
                ["name"] = SafeGetText(() => relic.Title),
                ["description"] = SafeGetText(() => relic.DynamicDescription),
                ["counter"] = relic.ShowCounter ? relic.DisplayAmount : null,
                ["keywords"] = BuildHoverTips(relic.HoverTipsExcludingRelic)
            });
        }
        state["relics"] = relics;

        // Potions
        var potions = new List<Dictionary<string, object?>>();
        int slotIndex = 0;
        foreach (var potion in player.PotionSlots)
        {
            if (potion != null)
            {
                potions.Add(new Dictionary<string, object?>
                {
                    ["id"] = potion.Id.Entry,
                    ["name"] = SafeGetText(() => potion.Title),
                    ["description"] = SafeGetText(() => potion.DynamicDescription),
                    ["slot"] = slotIndex,
                    ["can_use_in_combat"] = potion.Usage == PotionUsage.CombatOnly || potion.Usage == PotionUsage.AnyTime,
                    ["target_type"] = potion.TargetType.ToString(),
                    ["keywords"] = BuildHoverTips(potion.ExtraHoverTips)
                });
            }
            slotIndex++;
        }
        state["potions"] = potions;
        state["max_potion_slots"] = player.MaxPotionCount;

        return state;
    }

    private static string GetCostDisplay(CardModel card)
        => card.EnergyCost.CostsX ? "X" : card.EnergyCost.GetAmountToSpend().ToString();

    private static string? GetStarCostDisplay(CardModel card)
    {
        if (card.HasStarCostX) return "X";
        if (card.CurrentStarCost >= 0) return card.GetStarCostWithModifiers().ToString();
        return null;
    }

    /// <summary>
    /// Builds the common card display fields shared across all card serialization contexts.
    /// Callers merge context-specific fields (e.g. index, can_play, target_type) on top.
    /// </summary>
    private static Dictionary<string, object?> BuildCardInfo(CardModel card, PileType pile = PileType.None)
    {
        var info = new Dictionary<string, object?>
        {
            ["id"] = card.Id.Entry,
            ["name"] = SafeGetText(() => card.Title),
            ["type"] = card.Type.ToString(),
            ["cost"] = GetCostDisplay(card),
            ["star_cost"] = GetStarCostDisplay(card),
            ["description"] = SafeGetCardDescription(card, pile),
            ["rarity"] = card.Rarity.ToString(),
            ["is_upgraded"] = card.IsUpgraded,
            ["keywords"] = BuildHoverTips(card.HoverTips)
        };

        // GItS LOCAL EDIT (`EB-181`). A CARD FACE CARRIED NO ENCHANTMENT AT
        // ALL. `is_upgraded` is on the wire and an enchantment is not, so run
        // B6's Sharp *Water's Edge* reached NONE of the fields that exist and
        // a hand holding an enchanted copy beside a plain one was two
        // identical faces to every reader -- the blind page had to say so in
        // words (`HAND_REPEAT_NOTE`) because it could not say which.
        //
        // `CardModel.Enchantment` is the game's own property and is null on
        // almost every card, so the key is EMITTED ONLY WHEN THERE IS ONE:
        // an absent key means "not enchanted" and every board that was not
        // stays the size it was. `Amount` rides beside the name because an
        // enchantment can stack, and `shows_amount` is the game's own
        // `ShowAmount` -- whether the number is one a player is shown at all,
        // which is not for this bridge to decide.
        if (GitsEnchantmentInfo(card) is { } enchantment)
        {
            info["enchantment"] = enchantment;
        }
        return info;
    }

    /// <summary>
    /// `{ id, name, description, amount, shows_amount }` for an enchanted
    /// card, or null when the card carries none (`EB-181`). Never throws: it
    /// runs inside every card serialisation on every state poll, including the
    /// compendium's canonical copies.
    /// </summary>
    private static Dictionary<string, object?>? GitsEnchantmentInfo(CardModel card)
    {
        try
        {
            var enchantment = card.Enchantment;
            if (enchantment == null) return null;
            return new Dictionary<string, object?>
            {
                ["id"] = enchantment.Id.Entry,
                ["name"] = SafeGetText(() => enchantment.Title),
                ["description"] = SafeGetText(() => enchantment.DynamicDescription),
                ["amount"] = enchantment.DisplayAmount,
                ["shows_amount"] = enchantment.ShowAmount
            };
        }
        catch (Exception)
        {
            return null;
        }
    }

    private static Dictionary<string, object?> BuildCardState(CardModel card, int index)
    {
        // GItS LOCAL EDIT (`EB-748`). The second out parameter is WHAT
        // REFUSED, and both of this bridge's `CanPlay` calls used to discard
        // it -- which is why a Smoggy refusal reached the blind page as
        // "something else on the board is stopping you". Boxed to `object?`
        // deliberately: nothing in `gits/GitsRefusalSource.cs` names a game
        // type, so this edit cannot break on a signature it does not own.
        card.CanPlay(out var unplayableReason, out var refusedBy);
        object? gitsRefusedBy = refusedBy;

        var state = BuildCardInfo(card);
        state["index"] = index;
        state["description"] = SafeGetCardDescription(card); // hand cards use default pile
        state["target_type"] = card.TargetType.ToString();
        // GItS LOCAL EDIT (`EB-216`, the Kokomi draft-6 half). A CUSTOM target
        // type has no enum NAME -- BaseLib mints the value at ModelDb.Init, so
        // `ToString()` renders a bare number -- and the three the Plan uses
        // (`Pet`, `PetOrSelf`, the arm's `PetOrEnemy`) are exactly the ones a
        // seat has to be able to read. Rather than teach the bridge the mod's
        // enum table, this asks the CARD the question the UI asks it:
        // `IsValidTarget` is the game's own gate and BaseLib prefixes it for
        // every custom type, so a `true` here means the drag would land.
        state["can_target_pet"] = GitsCanTargetPet(card);
        // GItS LOCAL EDIT (`EB-402`). The same question about the other side of
        // the board, and it is what tells `PetOrEnemy` from `PetOrSelf` and
        // `Pet` -- all three of which render as the same bare number above. A
        // bare play of a `PetOrEnemy` card posts a NULL target, the card throws
        // on its own null check, and the wire answers `ok` for a no-op.
        state["can_target_enemy"] = GitsCanTargetEnemy(card);
        state["can_play"] = unplayableReason == UnplayableReason.None;
        state["unplayable_reason"] = unplayableReason != UnplayableReason.None ? unplayableReason.ToString() : null;

        // GItS LOCAL EDIT (the Klee Sparks arm). `cost` above is the ENERGY
        // cost, which is 0 for every Spark-priced card, and `can_play` collapses
        // every reason a card is unplayable into one boolean -- so without these
        // two an observed board shows a hand of free cards and cannot tell a
        // short bank from a missing target. Emitted only when the card actually
        // charges Sparks, so an ABSENT pair means "charges none" and the board
        // stays the size it was. Implementation and its reflection contract:
        // gits/GitsSparkPrice.cs; read by understudy/adapter.py.
        if (GitsSparkPrice(card) is { } sparkPrice)
        {
            state["spark_price"] = sparkPrice;
            state["spark_affordable"] = GitsSparkAffordable(card);
        }

        // GItS LOCAL EDIT (EB-264). `unplayable_reason` above is the game's own
        // enum, and `BlockedByCardLogic` -- the value EVERY mod-side gate
        // produces -- names no reason at all; the blind render printed it
        // verbatim at a tester holding a Spark-priced card with an empty bank.
        // The mod answers the same question in words. Emitted only when the
        // game has already refused the card AND the mod has something to say,
        // so an ABSENT key means "no sentence available" and the enum beside it
        // is unchanged for every reader that already asserts on it.
        // Implementation and its reflection contract: gits/GitsSparkPrice.cs.
        // `EB-748`: and where the mod has nothing to say, the GAME's own
        // preventer is named instead. The mod's sentence wins where it exists
        // -- it knows the price and the bank, which a class name cannot --
        // and this is the fallback under it, so the general case ("a power on
        // the board refused this") stops being the one refusal that names
        // nothing.
        if (unplayableReason != UnplayableReason.None)
        {
            var unplayableText = GitsUnplayableReasonText(card)
                                 ?? GitsRefusalSource(gitsRefusedBy);
            if (unplayableText != null)
            {
                state["unplayable_reason_text"] = unplayableText;
            }
        }

        return state;
    }

    private static void AddPreviewCardsFromContainer(
        Godot.Control? container,
        List<Dictionary<string, object?>> previewCards)
    {
        if (container?.Visible != true)
            return;

        var cardHolders = FindAllSortedByPosition<NCardHolder>(container);
        if (cardHolders.Count > 0)
        {
            foreach (var holder in cardHolders)
            {
                var card = holder.CardModel;
                if (card == null) continue;

                var cardInfo = BuildCardInfo(card);
                cardInfo["index"] = previewCards.Count;
                previewCards.Add(cardInfo);
            }
            return;
        }

        foreach (var holder in FindAll<NPreviewCardHolder>(container))
        {
            var card = holder.CardModel;
            if (card == null) continue;

            var cardInfo = BuildCardInfo(card);
            cardInfo["index"] = previewCards.Count;
            previewCards.Add(cardInfo);
        }
    }

    private static List<Dictionary<string, object?>> BuildPileCardList(IEnumerable<CardModel> cards, PileType pile)
    {
        var list = new List<Dictionary<string, object?>>();
        foreach (var card in cards)
        {
            // Pile cards only need a subset - keep it lightweight
            list.Add(new Dictionary<string, object?>
            {
                ["name"] = SafeGetText(() => card.Title),
                ["cost"] = GetCostDisplay(card),
                ["star_cost"] = GetStarCostDisplay(card),
                ["description"] = SafeGetCardDescription(card, pile)
            });
        }
        return list;
    }

    private static Dictionary<string, object?> BuildEnemyState(Creature creature, Dictionary<string, int> entityCounts)
    {
        var monster = creature.Monster;
        string baseId = monster?.Id.Entry ?? "unknown";

        // Generate entity_id like "jaw_worm_0"
        if (!entityCounts.TryGetValue(baseId, out int count))
            count = 0;
        entityCounts[baseId] = count + 1;
        string entityId = $"{baseId}_{count}";

        var state = new Dictionary<string, object?>
        {
            ["entity_id"] = entityId,
            ["combat_id"] = creature.CombatId,
            ["name"] = SafeGetText(() => monster?.Title),
            ["hp"] = creature.CurrentHp,
            ["max_hp"] = creature.MaxHp,
            ["block"] = creature.Block,
            ["status"] = BuildPowersState(creature)
        };

        // Intents
        if (monster?.NextMove is MoveState moveState)
        {
            var intents = new List<Dictionary<string, object?>>();
            foreach (var intent in moveState.Intents)
            {
                var intentData = new Dictionary<string, object?>
                {
                    ["type"] = intent.IntentType.ToString()
                };

                // GItS LOCAL EDIT (`EB-323`). WHOSE SIDE THIS PART LANDS ON.
                // `Empower (Buff)` reached the page as a heading, a bracketed
                // kind and nothing else, on a board of three bodies (Klee r7).
                // No intent carries a TARGET -- the bodies arrive at
                // `MoveState.PerformMove` when the move resolves, which is
                // after the telegraph a reader is looking at -- but the SIDE
                // is settled by the game's own `IntentType` for twelve of its
                // fifteen values, and the bridge was dropping it. Absent on
                // the three that settle nothing. gits/GitsIntentBreakdown.cs.
                if (GitsIntentBreakdown.TargetSide(intent.IntentType.ToString())
                    is { } targetSide)
                {
                    intentData[GitsIntentBreakdown.TargetSideKey] = targetSide;
                }

                try
                {
                    var targets = creature.CombatState?.PlayerCreatures;
                    if (targets != null)
                    {
                        string label = intent.GetIntentLabel(targets, creature).GetFormattedText();
                        intentData["label"] = StripRichTextTags(label);

                        var hoverTip = intent.GetHoverTip(targets, creature);
                        if (hoverTip.Title != null)
                            intentData["title"] = StripRichTextTags(hoverTip.Title);
                        if (hoverTip.Description != null)
                            intentData["description"] = StripRichTextTags(hoverTip.Description);
                    }
                }
                catch { /* intent label may fail for some types */ }

                // GItS LOCAL EDIT (`EB-607`). HOW THE GAME ARRIVED AT THAT
                // NUMBER. Fossil Stalker read 12 before and after Strength 3
                // while Corpse Slug's moved (Klee r23 lane 1), and the label
                // above cannot tell the two apart: it is one figure with no
                // history. `AttackIntent.GetSingleDamage` makes exactly the
                // call below and throws away the `out` list of the models it
                // folded; this keeps all three answers. NOTHING IS RECOMPUTED
                // HERE -- the moment the bridge does arithmetic of its own, a
                // page can disagree with the icon beside it.
                // gits/GitsIntentBreakdown.cs.
                if (intent is AttackIntent attack)
                {
                    try
                    {
                        if (GitsAttackBreakdown(attack, creature) is { } breakdown)
                        {
                            intentData[GitsIntentBreakdown.BreakdownKey] = breakdown;
                        }
                    }
                    catch { /* a read that throws is not a breakdown */ }
                }

                intents.Add(intentData);
            }
            state["intents"] = intents;
        }

        return state;
    }

    /// <summary>
    /// GItS LOCAL EDIT (`EB-607`). The breakdown behind one attack intent's
    /// icon figure: the base the move declares, the number the game's hook
    /// phases arrived at, the repeat count, and the models the game folded in.
    ///
    /// THIS IS `AttackIntent.GetSingleDamage`, CALL FOR CALL (decompiled,
    /// sts2.dll 0.111.0 `41cef1ea`), with the one difference that it keeps the
    /// `out` list the game discards. The order the phases compose in is
    /// written out on `klee-mod/KleeCode/Powers/HitOrder.cs` and is not
    /// repeated here, because this method does not reproduce it: it asks the
    /// game.
    ///
    /// NULL WHENEVER THE GAME'S OWN PRECONDITION FAILS -- no local player,
    /// which is what `GetSingleDamage` guards on -- so the wire key stays
    /// ABSENT rather than carrying a base with no fold beside it.
    /// </summary>
    private static Dictionary<string, object?>? GitsAttackBreakdown(
        AttackIntent intent, Creature owner)
    {
        var calc = intent.DamageCalc;
        if (calc == null) return null;
        int baseDamage = Math.Max(0, (int)calc());
        var me = LocalContext.GetMe(owner.CombatState);
        if (me == null) return null;

        decimal folded = Hook.ModifyDamage(
            me.RunState, me.Creature.CombatState, me.Creature, owner,
            calc(), ValueProp.Move, null, null, ModifyDamageHookType.All,
            CardPreviewMode.None, out IEnumerable<AbstractModel> modifiers);

        var names = new List<string>();
        foreach (var model in modifiers ?? Enumerable.Empty<AbstractModel>())
        {
            if (model == null) continue;
            // `gits/GitsRefusalSource.cs`'s namer, reused rather than forked:
            // a model's own printed Title where it has one, else its class
            // name as words. It is the nearest thing to a printed name a
            // reflection reader can honestly offer, and the refusal line on
            // the same page already uses it, so `Smoggy` reads as `Smoggy` in
            // both places.
            var name = GitsRefusalName(model, model.GetType());
            if (!string.IsNullOrWhiteSpace(name)) names.Add(name!);
        }

        return GitsIntentBreakdown.Compose(
            baseDamage, Math.Max(0, (int)folded), intent.Repeats, names);
    }

    private static Dictionary<string, object?> BuildEventState(EventRoom eventRoom, RunState runState)
    {
        var state = new Dictionary<string, object?>();

        var eventModel = eventRoom.CanonicalEvent;
        bool isAncient = eventModel is AncientEventModel;
        state["event_id"] = eventModel.Id.Entry;
        state["event_name"] = SafeGetText(() => eventModel.Title);
        state["is_ancient"] = isAncient;

        // Check dialogue state for ancients
        bool inDialogue = false;
        var uiRoom = NEventRoom.Instance;
        if (isAncient && uiRoom != null)
        {
            var ancientLayout = FindFirst<NAncientEventLayout>(uiRoom);
            if (ancientLayout != null)
            {
                var hitbox = ancientLayout.GetNodeOrNull<NClickableControl>("%DialogueHitbox");
                inDialogue = hitbox != null && hitbox.Visible && hitbox.IsEnabled;
            }
        }
        state["in_dialogue"] = inDialogue;

        // Event body text
        state["body"] = SafeGetText(() => eventModel.Description);

        // Options from UI
        var options = new List<Dictionary<string, object?>>();
        if (uiRoom != null)
        {
            var buttons = FindAll<NEventOptionButton>(uiRoom);
            int index = 0;
            foreach (var button in buttons)
            {
                var opt = button.Option;
                var optData = new Dictionary<string, object?>
                {
                    ["index"] = index,
                    ["title"] = SafeGetText(() => opt.Title),
                    ["description"] = SafeGetText(() => opt.Description),
                    ["is_locked"] = opt.IsLocked,
                    ["is_proceed"] = opt.IsProceed,
                    ["was_chosen"] = opt.WasChosen
                };
                if (opt.Relic != null)
                {
                    optData["relic_name"] = SafeGetText(() => opt.Relic.Title);
                    optData["relic_description"] = SafeGetText(() => opt.Relic.DynamicDescription);
                }
                optData["keywords"] = BuildHoverTips(opt.HoverTips);
                options.Add(optData);
                index++;
            }
        }
        // GItS LOCAL EDIT (`EB-682`). THE ROOM THAT PRINTED NO CHOICES AND HAD
        // THREE. The act-2 Ancient room (Tezcatara, Kokomi r27 lane 1) sent a
        // heading and an empty `options`, the blind page printed the heading
        // and its no-Proceed note with nothing between them, and the seat --
        // who called it "the most serious defect I hit" -- typed `choose 1` on
        // a guess and was handed Very Hot Cocoa. A seat that had trusted the
        // page would have called the room stuck. r32 met the same thing in the
        // Pael room.
        //
        // THE BUTTONS ARE A UI READ AND THE OPTIONS ARE NOT. `FindAll` walks
        // the live scene under `NEventRoom.Instance`, so a layout that has not
        // built its buttons yet -- an Ancient room animates them in after its
        // dialogue (`NAncientEventLayout.AnimateButtonsIn`) -- answers none,
        // while `EventModel.CurrentOptions` is the list the room is actually
        // offering and the list those buttons are built FROM, in that order.
        // `ExecuteChooseEventOption` still indexes the buttons, which is why
        // this fallback preserves their order and does not renumber anything:
        // it is the same rows, read one layer down, and the seat's `choose 1`
        // proves the click lands.
        //
        // ONLY WHERE THE UI READ FOUND NOTHING, so every screen that already
        // worked is byte-identical, and `from_model` marks the row as read off
        // the model rather than off a live button.
        if (options.Count == 0)
        {
            // GItS LOCAL EDIT (live look 8b, 2026-09-16). GUARDED, because
            // `LocalMutableEvent` is `EventSynchronizer.GetLocalEvent()` and
            // that is an unguarded index into a private array: two `get_state`
            // calls on the Furina run died with `ArgumentOutOfRangeException`
            // at `GetEventForPlayer`, losing the WHOLE screen rather than the
            // options. gits/GitsLocalEvent.cs carries the reasoning and logs
            // once; the fallback is the room's own canonical event, which is
            // what every other field on this screen is read off.
            var liveEvent =
                GitsLocalEvent.OrNothing(() => eventRoom.LocalMutableEvent)
                ?? eventModel;
            int index = 0;
            foreach (var opt in GitsModelEventOptions(liveEvent))
            {
                if (opt == null) continue;
                var optData = new Dictionary<string, object?>
                {
                    ["index"] = index,
                    ["title"] = SafeGetText(() => opt.Title),
                    ["description"] = SafeGetText(() => opt.Description),
                    ["is_locked"] = opt.IsLocked,
                    ["is_proceed"] = opt.IsProceed,
                    ["was_chosen"] = opt.WasChosen,
                    ["from_model"] = true
                };
                if (opt.Relic != null)
                {
                    optData["relic_name"] = SafeGetText(() => opt.Relic.Title);
                    optData["relic_description"] = SafeGetText(() => opt.Relic.DynamicDescription);
                }
                optData["keywords"] = BuildHoverTips(opt.HoverTips);
                options.Add(optData);
                index++;
            }
        }
        state["options"] = options;

        return state;
    }

    /// <summary>
    /// GItS LOCAL ADDITION (`EB-682`). The options an event model is offering,
    /// or an empty list. A state read must never throw, and this one reaches
    /// past the UI into the run's own model, so the read is guarded and an
    /// event with nothing to say answers nothing -- which is the state the
    /// page already renders.
    /// </summary>
    private static IReadOnlyList<EventOption> GitsModelEventOptions(EventModel? model)
    {
        if (model == null) return Array.Empty<EventOption>();
        try
        {
            return model.CurrentOptions ?? (IReadOnlyList<EventOption>)Array.Empty<EventOption>();
        }
        catch (Exception)
        {
            return Array.Empty<EventOption>();
        }
    }

    private static Dictionary<string, object?> BuildFakeMerchantState(EventRoom eventRoom, RunState runState)
    {
        var state = new Dictionary<string, object?>();
        // LocalMutableEvent holds the per-player mutable copy with populated inventory;
        // CanonicalEvent is the shared template which may not have it.
        var fakeMerchant = (FakeMerchant)(eventRoom.LocalMutableEvent ?? eventRoom.CanonicalEvent);

        state["event_id"] = fakeMerchant.Id.Entry;
        state["event_name"] = SafeGetText(() => fakeMerchant.Title);
        state["started_fight"] = fakeMerchant.StartedFight;

        // Find the NFakeMerchant UI node
        var uiRoom = NEventRoom.Instance;
        NFakeMerchant? fakeMerchantNode = null;
        if (uiRoom != null)
            fakeMerchantNode = FindFirst<NFakeMerchant>(uiRoom);

        if (fakeMerchant.StartedFight)
        {
            // After the foul potion fight, merchant is gone - just show proceed
            state["shop"] = new Dictionary<string, object?>
            {
                ["items"] = new List<Dictionary<string, object?>>(),
                ["can_proceed"] = true
            };
            state["message"] = "The fake merchant has been defeated. Proceed to map.";
            return state;
        }

        // Auto-open the inventory if the merchant button is still available
        if (fakeMerchantNode != null)
        {
            var inventoryUI = FindFirst<NMerchantInventory>(fakeMerchantNode);
            if (inventoryUI != null && !inventoryUI.IsOpen)
            {
                // ForceClick the merchant button to go through the proper signal chain
                // (disables proceed button, wires InventoryClosed callback, etc.)
                var merchantButton = fakeMerchantNode.MerchantButton;
                if (merchantButton != null && merchantButton.Visible && merchantButton.IsEnabled)
                    merchantButton.ForceClick();
            }
        }

        // Build shop inventory from the FakeMerchant model
        var shopState = BuildFakeMerchantShopItems(fakeMerchant.Inventory);

        // Proceed button
        if (fakeMerchantNode != null)
        {
            var proceedButton = FindFirst<NProceedButton>(fakeMerchantNode);
            shopState["can_proceed"] = proceedButton?.IsEnabled ?? false;
        }
        else
        {
            shopState["can_proceed"] = false;
        }

        state["shop"] = shopState;
        return state;
    }

    private static Dictionary<string, object?> BuildFakeMerchantShopItems(MerchantInventory? inventory)
    {
        var state = new Dictionary<string, object?>();

        if (inventory == null)
        {
            state["items"] = new List<Dictionary<string, object?>>();
            state["error"] = "Fake merchant inventory is not ready yet; retry in a moment.";
            return state;
        }

        var items = new List<Dictionary<string, object?>>();
        int index = 0;

        // FakeMerchant only sells relics (no cards, potions, or card removal)
        foreach (var entry in inventory.RelicEntries)
        {
            var item = new Dictionary<string, object?>
            {
                ["index"] = index,
                ["category"] = "relic",
                ["price"] = entry.Cost,
                ["is_stocked"] = entry.IsStocked,
                ["can_afford"] = entry.EnoughGold
            };
            if (entry.Model is { } relic)
            {
                item["relic_id"] = relic.Id.Entry;
                item["relic_name"] = SafeGetText(() => relic.Title);
                item["relic_description"] = SafeGetText(() => relic.DynamicDescription);
                item["keywords"] = BuildHoverTips(relic.HoverTipsExcludingRelic);
            }
            items.Add(item);
            index++;
        }

        state["items"] = items;
        return state;
    }

    private static Dictionary<string, object?> BuildRestSiteState(RestSiteRoom restSiteRoom, RunState runState)
    {
        var state = new Dictionary<string, object?>();

        var options = new List<Dictionary<string, object?>>();
        int index = 0;
        foreach (var opt in restSiteRoom.Options)
        {
            options.Add(new Dictionary<string, object?>
            {
                ["index"] = index,
                ["id"] = opt.OptionId,
                ["name"] = SafeGetText(() => opt.Title),
                ["description"] = SafeGetText(() => opt.Description),
                ["is_enabled"] = opt.IsEnabled
            });
            index++;
        }
        state["options"] = options;

        var proceedButton = NRestSiteRoom.Instance?.ProceedButton;
        state["can_proceed"] = proceedButton?.IsEnabled ?? false;

        return state;
    }

    private static Dictionary<string, object?> BuildShopState(MerchantRoom merchantRoom, RunState runState)
    {
        var state = new Dictionary<string, object?>();

        var inventory = merchantRoom.GetLocalInventory();
        if (inventory == null)
        {
            state["items"] = new List<Dictionary<string, object?>>();
            state["can_proceed"] = NMerchantRoom.Instance?.ProceedButton?.IsEnabled ?? false;
            state["error"] =
                "Shop inventory is not ready yet (null). Often happens right after entering the merchant from the map; retry in a moment.";
            return state;
        }

        var items = new List<Dictionary<string, object?>>();
        int index = 0;

        // Cards
        foreach (var entry in inventory.CardEntries)
        {
            var item = new Dictionary<string, object?>
            {
                ["index"] = index,
                ["category"] = "card",
                ["price"] = entry.Cost,
                ["is_stocked"] = entry.IsStocked,
                ["can_afford"] = entry.EnoughGold,
                ["on_sale"] = entry.IsOnSale
            };
            if (entry.CreationResult?.Card is { } card)
            {
                var cardInfo = BuildCardInfo(card);
                item["card_id"] = cardInfo["id"];
                item["card_name"] = cardInfo["name"];
                item["card_type"] = cardInfo["type"];
                item["card_cost"] = cardInfo["cost"];
                item["card_star_cost"] = cardInfo["star_cost"];
                item["card_rarity"] = cardInfo["rarity"];
                item["card_description"] = cardInfo["description"];
                item["keywords"] = cardInfo["keywords"];
            }
            items.Add(item);
            index++;
        }

        // Relics
        foreach (var entry in inventory.RelicEntries)
        {
            var item = new Dictionary<string, object?>
            {
                ["index"] = index,
                ["category"] = "relic",
                ["price"] = entry.Cost,
                ["is_stocked"] = entry.IsStocked,
                ["can_afford"] = entry.EnoughGold
            };
            if (entry.Model is { } relic)
            {
                item["relic_id"] = relic.Id.Entry;
                item["relic_name"] = SafeGetText(() => relic.Title);
                item["relic_description"] = SafeGetText(() => relic.DynamicDescription);
                item["keywords"] = BuildHoverTips(relic.HoverTipsExcludingRelic);
            }
            items.Add(item);
            index++;
        }

        // Potions
        foreach (var entry in inventory.PotionEntries)
        {
            var item = new Dictionary<string, object?>
            {
                ["index"] = index,
                ["category"] = "potion",
                ["price"] = entry.Cost,
                ["is_stocked"] = entry.IsStocked,
                ["can_afford"] = entry.EnoughGold
            };
            if (entry.Model is { } potion)
            {
                item["potion_id"] = potion.Id.Entry;
                item["potion_name"] = SafeGetText(() => potion.Title);
                item["potion_description"] = SafeGetText(() => potion.DynamicDescription);
                item["keywords"] = BuildHoverTips(potion.ExtraHoverTips);
            }
            items.Add(item);
            index++;
        }

        // Card removal
        if (inventory.CardRemovalEntry is { } removal)
        {
            items.Add(new Dictionary<string, object?>
            {
                ["index"] = index,
                ["category"] = "card_removal",
                ["price"] = removal.Cost,
                ["is_stocked"] = removal.IsStocked,
                ["can_afford"] = removal.EnoughGold
            });
        }

        state["items"] = items;

        var proceedButton = NMerchantRoom.Instance?.ProceedButton;
        state["can_proceed"] = proceedButton?.IsEnabled ?? false;

        return state;
    }

    private static Dictionary<string, object?> BuildMapState(RunState runState)
    {
        var state = new Dictionary<string, object?>();

        var map = runState.Map;
        var visitedCoords = runState.VisitedMapCoords;

        // Current position
        if (visitedCoords.Count > 0)
        {
            var cur = visitedCoords[visitedCoords.Count - 1];
            state["current_position"] = new Dictionary<string, object?>
            {
                ["col"] = cur.col, ["row"] = cur.row,
                ["type"] = map.GetPoint(cur)?.PointType.ToString()
            };
        }

        // Visited path
        var visited = new List<Dictionary<string, object?>>();
        foreach (var coord in visitedCoords)
        {
            visited.Add(new Dictionary<string, object?>
            {
                ["col"] = coord.col, ["row"] = coord.row,
                ["type"] = map.GetPoint(coord)?.PointType.ToString()
            });
        }
        state["visited"] = visited;

        // Next options - read travelable state from UI nodes
        var nextOptions = new List<Dictionary<string, object?>>();
        var mapScreen = NMapScreen.Instance;
        if (mapScreen != null)
        {
            var travelable = FindAll<NMapPoint>(mapScreen)
                .Where(mp => mp.State == MapPointState.Travelable && mp.Point != null)
                .OrderBy(mp => mp.Point!.coord.col)
                .ToList();

            int index = 0;
            foreach (var nmp in travelable)
            {
                var pt = nmp.Point;
                var option = new Dictionary<string, object?>
                {
                    ["index"] = index,
                    ["col"] = pt.coord.col,
                    ["row"] = pt.coord.row,
                    ["type"] = pt.PointType.ToString()
                };

                // 1-level lookahead
                var children = pt.Children
                    .OrderBy(c => c.coord.col)
                    .Select(c => new Dictionary<string, object?>
                    {
                        ["col"] = c.coord.col, ["row"] = c.coord.row,
                        ["type"] = c.PointType.ToString()
                    }).ToList();
                if (children.Count > 0)
                    option["leads_to"] = children;

                nextOptions.Add(option);
                index++;
            }
        }
        state["next_options"] = nextOptions;

        // Full map - all nodes organized for planning
        var nodes = new List<Dictionary<string, object?>>();

        // Starting point
        var start = map.StartingMapPoint;
        nodes.Add(BuildMapNode(start));

        // Grid nodes
        foreach (var pt in map.GetAllMapPoints())
            nodes.Add(BuildMapNode(pt));

        // Boss identity comes from the live act's EncounterModel — BossEncounter
        // throws if the act hasn't finished setup yet, so guard the access.
        EncounterModel? bossEncounter = null;
        try { bossEncounter = runState.Act.BossEncounter; } catch { }
        var secondBossEncounter = runState.Act.SecondBossEncounter;

        var primaryBossId = bossEncounter?.Id?.Entry;
        var primaryBossName = SafeGetText(() => bossEncounter?.Title);
        var bossNode = BuildMapNode(map.BossMapPoint);
        AddBossIdentity(bossNode, primaryBossId, primaryBossName);
        nodes.Add(bossNode);

        Dictionary<string, object?>? secondBoss = null;
        if (map.SecondBossMapPoint != null)
        {
            var secondBossId = secondBossEncounter?.Id?.Entry;
            var secondBossName = SafeGetText(() => secondBossEncounter?.Title);
            var secondBossNode = BuildMapNode(map.SecondBossMapPoint);
            AddBossIdentity(secondBossNode, secondBossId, secondBossName);
            nodes.Add(secondBossNode);
            secondBoss = BuildBossInfo(map.SecondBossMapPoint, secondBossId, secondBossName);
        }

        state["nodes"] = nodes;
        var primaryBoss = BuildBossInfo(map.BossMapPoint, primaryBossId, primaryBossName);
        state["boss"] = primaryBoss;
        state["bosses"] = secondBoss != null
            ? new List<Dictionary<string, object?>> { primaryBoss, secondBoss }
            : new List<Dictionary<string, object?>> { primaryBoss };

        return state;
    }

    private static Dictionary<string, object?> BuildBossInfo(MapPoint pt, string? bossId, string? bossName)
    {
        var boss = new Dictionary<string, object?>
        {
            ["col"] = pt.coord.col,
            ["row"] = pt.coord.row
        };
        AddBossIdentity(boss, bossId, bossName);
        return boss;
    }

    private static void AddBossIdentity(Dictionary<string, object?> target, string? bossId, string? bossName)
    {
        if (string.IsNullOrWhiteSpace(bossId))
            return;

        target["id"] = bossId;
        if (!string.IsNullOrWhiteSpace(bossName))
            target["name"] = bossName;
    }

    private static Dictionary<string, object?> BuildMapNode(MapPoint pt)
    {
        return new Dictionary<string, object?>
        {
            ["col"] = pt.coord.col,
            ["row"] = pt.coord.row,
            ["type"] = pt.PointType.ToString(),
            ["children"] = pt.Children
                .OrderBy(c => c.coord.col)
                .Select(c => new List<int> { c.coord.col, c.coord.row })
                .ToList()
        };
    }

    private static Dictionary<string, object?> BuildRewardsState(NRewardsScreen rewardsScreen, RunState runState)
    {
        var state = new Dictionary<string, object?>();

        // Reward items
        var rewardButtons = FindAll<NRewardButton>(rewardsScreen);
        var items = new List<Dictionary<string, object?>>();
        int index = 0;
        foreach (var button in rewardButtons)
        {
            if (button.Reward == null || !button.IsEnabled) continue;
            var reward = button.Reward;

            var item = new Dictionary<string, object?>
            {
                ["index"] = index,
                ["type"] = GetRewardTypeName(reward),
                ["description"] = SafeGetText(() => reward.Description)
            };

            // Type-specific details
            if (reward is GoldReward goldReward)
                item["gold_amount"] = goldReward.Amount;
            else if (reward is PotionReward potionReward && potionReward.Potion != null)
            {
                item["potion_id"] = potionReward.Potion.Id.Entry;
                item["potion_name"] = SafeGetText(() => potionReward.Potion.Title);
                item["potion_description"] = SafeGetText(() => potionReward.Potion.DynamicDescription);
            }
            // GItS LOCAL EDIT (`EB-716`, the relic half). A RELIC REWARD SENT
            // ITS NAME AND NOTHING ELSE. `Reward.Description` for a
            // `RelicReward` IS `_relic.Title` (decompiled), so a relic offer
            // reached the blind page as `{"type": "relic", "description":
            // "Golden Pearl"}` -- a name with no rules text, on a screen where
            // the chest one room over prints both, and beside a potion that
            // has carried its own text since this method was written.
            //
            // Same shape as the potion above and as `BuildShopState`'s relic
            // shelf, which is the prefixed convention every reader on the page
            // already follows. `Relic` is null on a reward that has not been
            // populated yet (`IsPopulated` IS `_relic != null`; an elite's
            // relic is rolled in `Populate`), so an ABSENT key means "not
            // rolled yet" and that row is exactly what it was.
            else if (reward is RelicReward relicReward && relicReward.Relic != null)
            {
                item["relic_id"] = relicReward.Relic.Id.Entry;
                item["relic_name"] = SafeGetText(() => relicReward.Relic.Title);
                item["relic_description"] = SafeGetText(() => relicReward.Relic.DynamicDescription);
            }

            items.Add(item);
            index++;
        }
        state["items"] = items;

        // Proceed button
        var proceedButton = FindFirst<NProceedButton>(rewardsScreen);
        state["can_proceed"] = proceedButton?.IsEnabled ?? false;

        return state;
    }

    private static Dictionary<string, object?> BuildCardRewardState(NCardRewardSelectionScreen cardScreen)
    {
        var state = new Dictionary<string, object?>();

        var cardHolders = FindAllSortedByPosition<NCardHolder>(cardScreen);
        var cards = new List<Dictionary<string, object?>>();
        int index = 0;
        foreach (var holder in cardHolders)
        {
            var card = holder.CardModel;
            if (card == null) continue;

            var cardInfo = BuildCardInfo(card);
            cardInfo["index"] = index;
            cards.Add(cardInfo);
            index++;
        }
        state["cards"] = cards;

        var altButtons = FindAll<NCardRewardAlternativeButton>(cardScreen);
        state["can_skip"] = altButtons.Count > 0;

        // GItS LOCAL EDIT (`EB-374`). AND WHAT EACH OF THOSE BUTTONS SAYS.
        //
        // THE FIND (Klee r9, act 2). Pael's Wing adds a SACRIFICE option to
        // this screen, and two card rewards in that run printed `choose` and
        // `skip` and nothing else -- the seat was holding the relic whose
        // whole rule is that button and never saw it. The bridge was counting
        // the buttons and throwing their words away, which is the line
        // directly above this one.
        //
        // The words, and the read order behind them: gits/GitsRewardAlternatives.cs.
        // An unreadable button is published with a null `name` rather than
        // dropped, because "there is a control here and the feed will not say
        // what it does" is the caveat the page already prints and the count
        // has to keep matching what `skip_card_reward` can press.
        var alternatives = new List<Dictionary<string, object?>>();
        for (int i = 0; i < altButtons.Count; i++)
        {
            var button = altButtons[i];
            alternatives.Add(new Dictionary<string, object?>
            {
                ["index"] = i,
                ["name"] = GitsAlternativeName(button, () =>
                {
                    var label = button.GetNodeOrNull("Label");
                    if (label == null) return null;
                    var text = label.Get("text");
                    return text.VariantType != Godot.Variant.Type.Nil
                        ? StripRichTextTags(text.AsString())
                        : null;
                }),
            });
        }
        state[GitsAlternativesKey] = alternatives;

        return state;
    }

    private static Dictionary<string, object?> BuildCardSelectState(NCardGridSelectionScreen screen, RunState runState)
    {
        var state = new Dictionary<string, object?>();

        // Screen type
        state["screen_type"] = screen switch
        {
            NDeckTransformSelectScreen => "transform",
            NDeckUpgradeSelectScreen => "upgrade",
            NDeckCardSelectScreen => "select",
            NSimpleCardSelectScreen => "simple_select",
            // GItS LOCAL EDIT (`EB-263`). The enchant picker fell through to
            // `GetType().Name`, so the page named the screen
            // `NDeckEnchantSelectScreen` -- an internal class name at a blind
            // reader, and a spelling no other screen on this wire uses.
            NDeckEnchantSelectScreen => "enchant",
            _ => screen.GetType().Name
        };

        // Player summary
        // Prompt text from UI label
        var bottomLabel = screen.GetNodeOrNull("%BottomLabel");
        if (bottomLabel != null)
        {
            var textVariant = bottomLabel.Get("text");
            string? prompt = textVariant.VariantType != Godot.Variant.Type.Nil ? StripRichTextTags(textVariant.AsString()) : null;
            state["prompt"] = prompt;
        }

        // Cards in the grid (sorted by visual position - MoveToFront can reorder children)
        var cardHolders = FindAllSortedByPosition<NGridCardHolder>(screen);
        // GItS LOCAL EDIT (`EB-263`): the selection, read once for the screen.
        var selected = GitsSelectedCards(screen);

        // GItS LOCAL EDIT (`EB-350`). EVERY CARD IN THE GRID, NOT THE ONES
        // THAT FIT.
        //
        // THE FIND (Kokomi r4d act 2, 10; act 3, 4 and 5). The shop's Card
        // Removal grid printed exactly 25 rows against a 38-card deck and
        // again against a 29-card deck, and a Klee seat routed into an Elite
        // at 2/62 unseen because the screen it planned on was not the deck.
        //
        // THE 25 IS A VIEWPORT AND NOT A CAP. `NCardGrid` is virtualised: it
        // holds every card in `_cards` and allocates holders only for the rows
        // on screen, so the holder walk above is a screenshot. The full list
        // and why it is safe to index into: gits/GitsCardGrid.cs.
        //
        // THE INDICES DO NOT MOVE. `_cards` IS the grid's row order and the
        // window starts at row 0 when a screen opens, so the rows a page
        // already printed as 0..24 are `_cards[0..24]` exactly, and every row
        // past them is new. `McpMod.Actions.cs`'s `select_grid_card` reaches
        // those new rows through the screen's own `OnCardClicked`.
        var gridCards = GitsGridCards(screen);
        var cards = new List<Dictionary<string, object?>>();
        int index = 0;
        if (gridCards != null)
        {
            var onScreen = new HashSet<CardModel>();
            foreach (var holder in cardHolders)
            {
                if (holder.CardModel != null) onScreen.Add(holder.CardModel);
            }
            foreach (var entry in gridCards)
            {
                if (entry is not CardModel card) continue;
                var cardInfo = BuildCardInfo(card);
                cardInfo["index"] = index;
                cardInfo["selected"] = selected != null && selected.Contains(card);
                // Whether a holder is standing on this row right now. Not a
                // reader's business on the page, and it is the one fact that
                // says which half of the old feed a row came from.
                cardInfo["on_screen"] = onScreen.Contains(card);
                cards.Add(cardInfo);
                index++;
            }
        }
        else
        {
            foreach (var holder in cardHolders)
            {
                var card = holder.CardModel;
                if (card == null) continue;

                var cardInfo = BuildCardInfo(card);
                cardInfo["index"] = index;
                cardInfo["selected"] = selected != null && selected.Contains(card);
                cards.Add(cardInfo);
                index++;
            }
        }
        state["cards"] = cards;
        // Which of the two answered. "These are all the cards" and "these are
        // the cards that fit" are different claims, and a page that could not
        // tell them apart would print the second under the first's heading --
        // which is the r4d defect exactly.
        state[GitsGridCompleteKey] = gridCards != null;
        state[GitsGridTotalKey] = gridCards?.Count ?? cards.Count;
        // Whether the flag above is a READ or a default. `selected` is null
        // when the grid could not be asked, and a page that cannot tell
        // "nothing is selected" from "the feed does not know" would print the
        // first while meaning the second.
        state["selection_known"] = selected != null;

        // Preview container showing? (selection complete, awaiting confirm)
        // Upgrade screens use UpgradeSinglePreviewContainer / UpgradeMultiPreviewContainer
        var previewSingle = screen.GetNodeOrNull<Godot.Control>("%UpgradeSinglePreviewContainer");
        var previewMulti = screen.GetNodeOrNull<Godot.Control>("%UpgradeMultiPreviewContainer");
        var previewGeneric = screen.GetNodeOrNull<Godot.Control>("%PreviewContainer");
        // GItS LOCAL EDIT (`EB-263`). THE ENCHANT SCREEN OPENED NO PREVIEW.
        // `NDeckEnchantSelectScreen` names its two containers
        // `%EnchantSinglePreviewContainer` / `%EnchantMultiPreviewContainer`
        // (its `_Ready`), and neither spelling was looked up here -- so the
        // pick a tester had just made reached the page nowhere and `EB-263`
        // filed "the enchant picker offered no pick". Both hold
        // `NPreviewCardHolder`s: the single one holds the BEFORE card and the
        // enchanted AFTER card, in that tree order (`NEnchantPreview.Init`),
        // and the multi one holds one per selected card.
        var previewEnchantSingle = screen.GetNodeOrNull<Godot.Control>("%EnchantSinglePreviewContainer");
        var previewEnchantMulti = screen.GetNodeOrNull<Godot.Control>("%EnchantMultiPreviewContainer");
        bool previewShowing = (previewSingle?.Visible ?? false)
                            || (previewMulti?.Visible ?? false)
                            || (previewGeneric?.Visible ?? false)
                            || (previewEnchantSingle?.Visible ?? false)
                            || (previewEnchantMulti?.Visible ?? false);
        state["preview_showing"] = previewShowing;
        if (previewShowing)
        {
            var previewCards = new List<Dictionary<string, object?>>();
            AddPreviewCardsFromContainer(previewSingle, previewCards);
            AddPreviewCardsFromContainer(previewMulti, previewCards);
            AddPreviewCardsFromContainer(previewGeneric, previewCards);
            AddPreviewCardsFromContainer(previewEnchantSingle, previewCards);
            AddPreviewCardsFromContainer(previewEnchantMulti, previewCards);
            state["preview_cards"] = previewCards;
        }

        // Button states - when a preview is open, cancel goes through the
        // preview container's Cancel / PreviewCancel button (same path as
        // the action handler), not the top-level %Close button.
        bool canCancel = false;
        if (previewShowing)
        {
            foreach (var container in new[] { previewSingle, previewMulti, previewGeneric,
                                              previewEnchantSingle, previewEnchantMulti })
            {
                if (container?.Visible == true)
                {
                    var cancelBtn = container.GetNodeOrNull<NBackButton>("Cancel")
                                    ?? container.GetNodeOrNull<NBackButton>("%PreviewCancel");
                    if (cancelBtn?.IsEnabled == true) { canCancel = true; break; }
                }
            }
        }
        if (!canCancel)
        {
            var closeButton = screen.GetNodeOrNull<NBackButton>("%Close");
            canCancel = closeButton?.IsEnabled ?? false;
        }
        state["can_cancel"] = canCancel;

        // Confirm button - search all preview containers and main screen
        bool canConfirm = false;
        foreach (var container in new[] { previewSingle, previewMulti, previewGeneric,
                                          previewEnchantSingle, previewEnchantMulti })
        {
            if (container?.Visible == true)
            {
                var confirm = container.GetNodeOrNull<NConfirmButton>("Confirm")
                              ?? container.GetNodeOrNull<NConfirmButton>("%PreviewConfirm");
                if (confirm?.IsEnabled == true) { canConfirm = true; break; }
            }
        }
        if (!canConfirm)
        {
            var mainConfirm = screen.GetNodeOrNull<NConfirmButton>("Confirm")
                              ?? screen.GetNodeOrNull<NConfirmButton>("%Confirm");
            if (mainConfirm?.IsEnabled == true) canConfirm = true;
        }
        // Fallback: search entire screen tree for any enabled confirm button
        // (covers subclasses like NDeckEnchantSelectScreen)
        if (!canConfirm)
        {
            canConfirm = FindAll<NConfirmButton>(screen).Any(b => b.IsEnabled && b.IsVisibleInTree());
        }
        state["can_confirm"] = canConfirm;

        return state;
    }

    private static Dictionary<string, object?> BuildChooseCardState(NChooseACardSelectionScreen screen, RunState runState)
    {
        var state = new Dictionary<string, object?>();
        state["screen_type"] = "choose";

        state["prompt"] = "Choose a card.";

        var cardHolders = FindAllSortedByPosition<NGridCardHolder>(screen);
        var cards = new List<Dictionary<string, object?>>();
        int index = 0;
        foreach (var holder in cardHolders)
        {
            var card = holder.CardModel;
            if (card == null) continue;

            var cardInfo = BuildCardInfo(card);
            cardInfo["index"] = index;
            cards.Add(cardInfo);
            index++;
        }
        state["cards"] = cards;

        var skipButton = screen.GetNodeOrNull<NClickableControl>("SkipButton");
        state["can_skip"] = skipButton?.IsEnabled == true && skipButton.Visible;
        state["preview_showing"] = false;
        state["can_confirm"] = false;
        state["can_cancel"] = state["can_skip"];

        return state;
    }

    private static Dictionary<string, object?> BuildBundleSelectState(NChooseABundleSelectionScreen screen, RunState runState)
    {
        var state = new Dictionary<string, object?>();
        state["screen_type"] = "bundle";

        state["prompt"] = "Choose a bundle.";

        var bundles = new List<Dictionary<string, object?>>();
        int index = 0;
        foreach (var bundle in FindAll<NCardBundle>(screen))
        {
            var cards = new List<Dictionary<string, object?>>();
            int cardIndex = 0;
            foreach (var card in bundle.Bundle)
            {
                var cardInfo = BuildCardInfo(card);
                cardInfo["index"] = cardIndex;
                cards.Add(cardInfo);
                cardIndex++;
            }

            bundles.Add(new Dictionary<string, object?>
            {
                ["index"] = index,
                ["card_count"] = cards.Count,
                ["cards"] = cards
            });
            index++;
        }
        state["bundles"] = bundles;

        var previewContainer = screen.GetNodeOrNull<Godot.Control>("%BundlePreviewContainer");
        bool previewShowing = previewContainer?.Visible == true;
        state["preview_showing"] = previewShowing;

        var previewCards = new List<Dictionary<string, object?>>();
        var previewCardsContainer = screen.GetNodeOrNull<Godot.Control>("%Cards");
        if (previewCardsContainer != null)
        {
            int previewIndex = 0;
            foreach (var holder in FindAll<NPreviewCardHolder>(previewCardsContainer))
            {
                var card = holder.CardModel;
                if (card == null) continue;

                var cardInfo = BuildCardInfo(card);
                cardInfo["index"] = previewIndex;
                previewCards.Add(cardInfo);
                previewIndex++;
            }
        }
        state["preview_cards"] = previewCards;

        var cancelButton = screen.GetNodeOrNull<NBackButton>("%Cancel");
        var confirmButton = screen.GetNodeOrNull<NConfirmButton>("%Confirm");
        state["can_cancel"] = cancelButton?.IsEnabled == true;
        state["can_confirm"] = confirmButton?.IsEnabled == true;

        return state;
    }

    private static Dictionary<string, object?> BuildHandSelectState(NPlayerHand hand, RunState runState)
    {
        var state = new Dictionary<string, object?>();

        // Mode
        state["mode"] = hand.CurrentMode switch
        {
            NPlayerHand.Mode.SimpleSelect => "simple_select",
            NPlayerHand.Mode.UpgradeSelect => "upgrade_select",
            _ => hand.CurrentMode.ToString()
        };

        // Prompt text from %SelectionHeader
        var headerLabel = hand.GetNodeOrNull<Godot.Control>("%SelectionHeader");
        if (headerLabel != null)
        {
            var textVariant = headerLabel.Get("text");
            string? prompt = textVariant.VariantType != Godot.Variant.Type.Nil
                ? StripRichTextTags(textVariant.AsString())
                : null;
            state["prompt"] = prompt;
        }

        // Selectable cards (visible holders in the hand)
        var selectableCards = new List<Dictionary<string, object?>>();
        int index = 0;
        foreach (var holder in hand.ActiveHolders)
        {
            var card = holder.CardModel;
            if (card == null) continue;

            var cardInfo = BuildCardInfo(card);
            cardInfo["index"] = index;
            cardInfo["description"] = SafeGetCardDescription(card); // hand cards use default pile
            selectableCards.Add(cardInfo);
            index++;
        }
        state["cards"] = selectableCards;

        // Already-selected cards (in the SelectedHandCardContainer)
        var selectedContainer = hand.GetNodeOrNull<Godot.Control>("%SelectedHandCardContainer");
        if (selectedContainer != null)
        {
            var selectedCards = new List<Dictionary<string, object?>>();
            var selectedHolders = FindAll<NSelectedHandCardHolder>(selectedContainer);
            int selIdx = 0;
            foreach (var holder in selectedHolders)
            {
                var card = holder.CardModel;
                if (card == null) continue;
                selectedCards.Add(new Dictionary<string, object?>
                {
                    ["index"] = selIdx,
                    ["name"] = SafeGetText(() => card.Title)
                });
                selIdx++;
            }
            if (selectedCards.Count > 0)
                state["selected_cards"] = selectedCards;
        }

        // Confirm button state
        var confirmBtn = hand.GetNodeOrNull<NConfirmButton>("%SelectModeConfirmButton");
        state["can_confirm"] = confirmBtn?.IsEnabled ?? false;

        return state;
    }

    private static Dictionary<string, object?> BuildRelicSelectState(NChooseARelicSelection screen, RunState runState)
    {
        var state = new Dictionary<string, object?>();

        state["prompt"] = "Choose a relic.";

        var relicHolders = FindAll<NRelicBasicHolder>(screen);
        var relics = new List<Dictionary<string, object?>>();
        int index = 0;
        foreach (var holder in relicHolders)
        {
            var relic = holder.Relic?.Model;
            if (relic == null) continue;

            relics.Add(new Dictionary<string, object?>
            {
                ["index"] = index,
                ["id"] = relic.Id.Entry,
                ["name"] = SafeGetText(() => relic.Title),
                ["description"] = SafeGetText(() => relic.DynamicDescription),
                ["rarity"] = relic.Rarity.ToString(),
                ["keywords"] = BuildHoverTips(relic.HoverTipsExcludingRelic)
            });
            index++;
        }
        state["relics"] = relics;

        var skipButton = screen.GetNodeOrNull<NClickableControl>("SkipButton");
        state["can_skip"] = skipButton?.IsEnabled == true && skipButton.Visible;

        return state;
    }

    private static Dictionary<string, object?> BuildCrystalSphereState(NCrystalSphereScreen screen, RunState runState)
    {
        var state = new Dictionary<string, object?>();

        var instructionsTitle = screen.GetNodeOrNull<Godot.Control>("%InstructionsTitle");
        if (instructionsTitle != null)
        {
            var textVariant = instructionsTitle.Get("text");
            if (textVariant.VariantType != Godot.Variant.Type.Nil)
                state["instructions_title"] = StripRichTextTags(textVariant.AsString());
        }

        var instructionsDescription = screen.GetNodeOrNull<Godot.Control>("%InstructionsDescription");
        if (instructionsDescription != null)
        {
            var textVariant = instructionsDescription.Get("text");
            if (textVariant.VariantType != Godot.Variant.Type.Nil)
                state["instructions_description"] = StripRichTextTags(textVariant.AsString());
        }

        var cells = FindAll<NCrystalSphereCell>(screen);
        state["grid_width"] = cells.Count > 0 ? cells.Max(c => c.Entity.X) + 1 : 0;
        state["grid_height"] = cells.Count > 0 ? cells.Max(c => c.Entity.Y) + 1 : 0;

        var cellStates = new List<Dictionary<string, object?>>();
        var clickableCells = new List<Dictionary<string, object?>>();
        foreach (var cell in cells.OrderBy(c => c.Entity.Y).ThenBy(c => c.Entity.X))
        {
            var cellState = new Dictionary<string, object?>
            {
                ["x"] = cell.Entity.X,
                ["y"] = cell.Entity.Y,
                ["is_hidden"] = cell.Entity.IsHidden,
                ["is_clickable"] = cell.Entity.IsHidden && cell.Visible,
                ["is_highlighted"] = cell.Entity.IsHighlighted,
                ["is_hovered"] = cell.Entity.IsHovered
            };

            if (!cell.Entity.IsHidden && cell.Entity.Item != null)
            {
                cellState["item_type"] = cell.Entity.Item.GetType().Name;
                cellState["is_good"] = cell.Entity.Item.IsGood;
            }

            cellStates.Add(cellState);
            if (cell.Entity.IsHidden && cell.Visible)
            {
                clickableCells.Add(new Dictionary<string, object?>
                {
                    ["x"] = cell.Entity.X,
                    ["y"] = cell.Entity.Y
                });
            }
        }
        state["cells"] = cellStates;
        state["clickable_cells"] = clickableCells;

        var revealedItems = new List<Dictionary<string, object?>>();
        foreach (var item in cells
                     .Where(c => !c.Entity.IsHidden && c.Entity.Item != null)
                     .Select(c => c.Entity.Item!)
                     .Distinct())
        {
            revealedItems.Add(new Dictionary<string, object?>
            {
                ["item_type"] = item.GetType().Name,
                ["x"] = item.Position.X,
                ["y"] = item.Position.Y,
                ["width"] = item.Size.X,
                ["height"] = item.Size.Y,
                ["is_good"] = item.IsGood
            });
        }
        state["revealed_items"] = revealedItems;

        var bigButton = screen.GetNodeOrNull<Godot.Control>("%BigDivinationButton");
        var smallButton = screen.GetNodeOrNull<Godot.Control>("%SmallDivinationButton");
        bool bigVisible = bigButton?.Visible == true;
        bool smallVisible = smallButton?.Visible == true;
        bool bigActive = bigButton?.GetNodeOrNull<Godot.Control>("%Outline")?.Visible == true;
        bool smallActive = smallButton?.GetNodeOrNull<Godot.Control>("%Outline")?.Visible == true;

        state["tool"] = bigActive ? "big" : smallActive ? "small" : "none";
        state["can_use_big_tool"] = bigVisible;
        state["can_use_small_tool"] = smallVisible;

        var divinationsLeft = screen.GetNodeOrNull<Godot.Control>("%DivinationsLeft");
        if (divinationsLeft != null)
        {
            var textVariant = divinationsLeft.Get("text");
            if (textVariant.VariantType != Godot.Variant.Type.Nil)
                state["divinations_left_text"] = StripRichTextTags(textVariant.AsString());
        }

        state["can_proceed"] = FindCrystalSphereProceedButton(screen) != null;

        return state;
    }

    private static Dictionary<string, object?> BuildTreasureState(TreasureRoom treasureRoom, RunState runState)
    {
        var state = new Dictionary<string, object?>();

        var treasureUI = FindFirst<NTreasureRoom>(
            ((Godot.SceneTree)Godot.Engine.GetMainLoop()).Root);

        if (treasureUI == null)
        {
            state["message"] = "Treasure room loading...";
            return state;
        }

        // Auto-open chest if not yet opened
        var chestButton = treasureUI.GetNodeOrNull<NClickableControl>("Chest");
        if (chestButton is { IsEnabled: true })
        {
            chestButton.ForceClick();
            state["message"] = "Opening chest...";
            return state;
        }

        // Show relics available for picking
        var relicCollection = treasureUI.GetNodeOrNull<NTreasureRoomRelicCollection>("%RelicCollection");
        if (relicCollection?.Visible == true)
        {
            var holders = FindAll<NTreasureRoomRelicHolder>(relicCollection)
                .Where(h => h.IsEnabled && h.Visible)
                .ToList();

            var relics = new List<Dictionary<string, object?>>();
            int index = 0;
            foreach (var holder in holders)
            {
                var relic = holder.Relic?.Model;
                if (relic == null) continue;
                relics.Add(new Dictionary<string, object?>
                {
                    ["index"] = index,
                    ["id"] = relic.Id.Entry,
                    ["name"] = SafeGetText(() => relic.Title),
                    ["description"] = SafeGetText(() => relic.DynamicDescription),
                    ["rarity"] = relic.Rarity.ToString(),
                    ["keywords"] = BuildHoverTips(relic.HoverTipsExcludingRelic)
                });
                index++;
            }
            state["relics"] = relics;
        }

        state["can_proceed"] = treasureUI.ProceedButton?.IsEnabled ?? false;

        return state;
    }

    private static string GetRewardTypeName(Reward reward) => reward switch
    {
        GoldReward => "gold",
        PotionReward => "potion",
        RelicReward => "relic",
        CardReward => "card",
        SpecialCardReward => "special_card",
        CardRemovalReward => "card_removal",
        _ => reward.GetType().Name.ToLower()
    };

    private static List<Dictionary<string, object?>> BuildPowersState(Creature creature)
    {
        var powers = new List<Dictionary<string, object?>>();
        foreach (var power in creature.Powers)
        {
            if (!power.IsVisible) continue;

            // Per-power try/catch: HoverTips getter calls into game engine code
            // (LocString resolution, DynamicVars, virtual ExtraHoverTips) that can
            // throw during state transitions. Skip the power rather than fail the
            // entire state query.
            try
            {
                var allTips = power.HoverTips.ToList();
                string? resolvedDesc = null;
                var extraTips = new List<IHoverTip>();
                foreach (var tip in allTips)
                {
                    if (tip.Id == power.Id.ToString())
                    {
                        if (tip is HoverTip ht && ht.Description != null)
                            resolvedDesc = StripRichTextTags(ht.Description);
                    }
                    else
                    {
                        extraTips.Add(tip);
                    }
                }
                resolvedDesc ??= SafeGetText(() => power.SmartDescription);

                powers.Add(new Dictionary<string, object?>
                {
                    ["id"] = power.Id.Entry,
                    ["name"] = SafeGetText(() => power.Title),
                    ["amount"] = power.DisplayAmount,
                    ["type"] = power.Type.ToString(),
                    ["description"] = resolvedDesc,
                    ["keywords"] = BuildHoverTips(extraTips)
                });
            }
            catch { /* skip this power - game engine state may be inconsistent */ }
        }
        return powers;
    }

    private static List<Dictionary<string, object?>> BuildPetsState(Player player)
    {
        var pets = new List<Dictionary<string, object?>>();
        var combatState = player.PlayerCombatState;
        if (combatState == null) return pets;

        // GItS LOCAL EDIT (`EB-216`, the Kokomi draft-6 half). EVERY PET, not
        // just Osty. Upstream checked Osty by type on the argument that
        // "Byrdpip/PaelsLegion are cosmetic with no real combat state", which
        // was true of the two pets that existed -- and stopped being true the
        // moment a mod pet became a TARGET. The Bake-Kurage is where a Plan is
        // sent, so a seat that cannot see it cannot play the character.
        //
        // `entity_id` IS THE COMBAT ID, as a string, and that is the whole
        // point of the field: `ResolveTarget` parses a numeric id straight
        // through `ICombatState.GetCreature`, so a pet is aimed at through
        // exactly the door an enemy is aimed at through. Osty keeps every
        // field it had and gains this one.
        // GItS LOCAL EDIT (`EB-735`). WHICH SEAT A PERFORMER IS STANDING IN.
        // A Furina Stage performer is a pet whose HP IS its Fanfare bar, and
        // the one fact a pet row cannot carry is its SEAT -- this list is in
        // the order the bodies were fielded, which a rotation and a departure
        // both break, while every rule in that kit is written against front
        // and back. Read off the arm's own ledger through the same snapshot
        // `state["furina_stage"]` is built from, so the two surfaces cannot
        // come to disagree; an empty map on every other board, which is every
        // board in a release build.
        var stageSeats = GitsFurinaStageSeats(player);
        foreach (var pet in combatState.Pets)
        {
            var petId = pet.CombatId.ToString() ?? string.Empty;
            var row = new Dictionary<string, object?>
            {
                ["id"] = pet.Monster?.Id.Entry ?? "PET",
                ["entity_id"] = petId,
                ["name"] = SafeGetText(() => pet.Monster?.Title) ?? "Pet",
                ["alive"] = pet.IsAlive,
                ["hp"] = pet.CurrentHp,
                ["max_hp"] = pet.MaxHp,
                ["block"] = pet.Block,
                ["status"] = BuildPowersState(pet)
            };
            if (stageSeats.TryGetValue(petId, out var seat))
            {
                row["stage_member"] = seat.Member;
                row["stage_seat"] = seat.Seat;
            }
            pets.Add(row);
        }

        return pets;
    }
}
