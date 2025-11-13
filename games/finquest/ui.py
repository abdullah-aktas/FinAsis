# -*- coding: utf-8 -*-
"""
UI helpers for FinQuest 3D.
All functions here accept the game instance and manipulate its UI elements.
"""
from ursina import Entity, Text, Button, camera, color, Vec3
from ursina import destroy  # type: ignore


def create_game_ui(game):
    """Create in-game HUD panels and quest list UI for the given game instance."""
    # Info panel
    game.info_panel = Entity(
        model='quad',
        scale=Vec3(0.3, 0.15, 1),
        position=Vec3(-0.6, 0.4, 0),
        color=color.rgba(0, 0, 0, 0.7),
        parent=camera.ui,
    )

    # Player info texts
    game.player_name = Text(
        text=f"İsim: {game.game_state['player']['company']['name']}",
        position=(-0.6, 0.45),
        origin=(0, 0),
        color=color.white,
        parent=camera.ui,
    )

    game.player_money = Text(
        text=f"Para: {game.game_state['player']['money']} ₺",
        position=(-0.6, 0.4),
        origin=(0, 0),
        color=color.white,
        parent=camera.ui,
    )

    game.player_level = Text(
        text=f"Seviye: {game.game_state['player']['level']}",
        position=(-0.6, 0.35),
        origin=(0, 0),
        color=color.white,
        parent=camera.ui,
    )

    # Date panel
    game.date_panel = Entity(
        model='quad',
        scale=Vec3(0.2, 0.05, 1),
        position=Vec3(0, 0.45, 0),
        color=color.rgba(0, 0, 0, 0.7),
        parent=camera.ui,
    )

    game.date_text = Text(
        text=(
            f"Gün: {game.game_state['time']['day']} | "
            f"Ay: {game.game_state['time']['month']} | "
            f"Yıl: {game.game_state['time']['year']}"
        ),
        position=(0, 0.45),
        origin=(0, 0),
        color=color.white,
        parent=camera.ui,
    )

    # Quest panel
    game.quest_panel = Entity(
        model='quad',
        scale=Vec3(0.3, 0.25, 1),
        position=Vec3(0.6, 0.35, 0),
        color=color.rgba(0, 0, 0, 0.7),
        parent=camera.ui,
    )

    game.quest_title = Text(
        text="GÖREVLER",
        position=(0.6, 0.45),
        origin=(0, 0),
        color=color.gold,
        parent=camera.ui,
    )

    game.quest_list_entity = Entity(
        parent=camera.ui,
        position=Vec3(0.6, 0.4, 0),
    )

    # Interaction prompt
    game.interaction_prompt = Text(
        text="",
        position=(0, -0.4),
        origin=(0, 0),
        color=color.white,
        parent=camera.ui,
        visible=False,
    )

    # Register for cleanup
    game.ui_elements['game'] = [
        game.info_panel,
        game.player_name,
        game.player_money,
        game.player_level,
        game.date_panel,
        game.date_text,
        game.quest_panel,
        game.quest_title,
        game.quest_list_entity,
        game.interaction_prompt,
    ]

    update_quest_list(game)


def update_quest_list(game):
    """Rebuild active quests list UI from the game state."""
    for child in list(game.quest_list_entity.children):
        destroy(child)

    y_position = 0
    for quest_id in game.game_state['active_quests']:
        quest_data = None
        for category, quests in game.quests.items():
            for quest in quests:
                if quest['id'] == quest_id:
                    quest_data = quest
                    break
            if quest_data:
                break
        if quest_data:
            Text(
                text=f"{quest_data['title']}: {quest_data['description']}",
                position=(0, y_position),
                origin=(0, 0),
                color=color.white,
                parent=game.quest_list_entity,
                scale=0.7,
            )
            y_position -= 0.05


def show_interaction_prompt(game, text):
    game.interaction_prompt.text = text
    game.interaction_prompt.visible = True


def hide_interaction_prompt(game):
    game.interaction_prompt.visible = False


def show_quest_completion(game, quest_data):
    panel = Entity(
        model='quad',
        scale=Vec3(0.5, 0.3, 1),
        position=Vec3(0, 0, 0),
        color=color.rgba(0, 0, 0, 0.8),
        parent=camera.ui,
    )

    Text(
        text="GÖREV TAMAMLANDI!",
        position=(0, 0.1),
        origin=(0, 0),
        color=color.gold,
        parent=panel,
    )

    Text(
        text=f"{quest_data['title']}\n{quest_data['description']}",
        position=(0, 0),
        origin=(0, 0),
        color=color.white,
        parent=panel,
    )

    Text(
        text=(
            f"Ödül: {quest_data['reward'].get('money', 0)} ₺ | "
            f"{quest_data['reward'].get('exp', 0)} XP"
        ),
        position=(0, -0.1),
        origin=(0, 0),
        color=color.green,
        parent=panel,
    )

    from ursina import invoke  # local import to match game file style
    def _close():
        destroy(panel)
    invoke(_close, delay=3)


def show_level_up(game):
    panel = Entity(
        model='quad',
        scale=Vec3(0.5, 0.3, 1),
        position=Vec3(0, 0, 0),
        color=color.rgba(0, 0, 0, 0.8),
        parent=camera.ui,
    )

    Text(
        text="SEVİYE ATLAMA!",
        position=(0, 0.1),
        origin=(0, 0),
        color=color.gold,
        parent=panel,
    )

    Text(
        text=f"Tebrikler! Seviye {game.game_state['player']['level']} oldunuz.",
        position=(0, 0),
        origin=(0, 0),
        color=color.white,
        parent=panel,
    )

    Text(
        text="Yeni seviyede ticaret kabiliyetiniz ve ürün çeşitliliğiniz arttı!",
        position=(0, -0.1),
        origin=(0, 0),
        color=color.green,
        parent=panel,
    )

    from ursina import invoke
    def _close():
        destroy(panel)
    invoke(_close, delay=3)


def create_demo_panels(game):
    """Demo: VR, NFT, AI NPC ve dünya paneli"""
    from ursina import Entity, Text, Button, camera, color, Vec3
    # VR panel
    game.vr_panel = Entity(
        model='quad',
        scale=Vec3(0.2, 0.07, 1),
        position=Vec3(-0.6, 0.25, 0),
        color=color.rgba(0, 212, 255, 180),
        parent=camera.ui,
    )
    game.vr_text = Text(
        text=f"VR Durumu: {game.demo.toggle_vr()}",
        position=(-0.6, 0.25),
        color=color.white,
        parent=camera.ui,
    )
    game.vr_button = Button(
        text="VR Aç/Kapat",
        position=(-0.6, 0.22),
        color=color.azure,
        parent=camera.ui,
        on_click=lambda: game.vr_text.set_text(f"VR Durumu: {game.demo.toggle_vr()}")
    )
    # NFT panel
    game.nft_panel = Entity(
        model='quad',
        scale=Vec3(0.2, 0.12, 1),
        position=Vec3(-0.6, 0.12, 0),
        color=color.rgba(0, 212, 255, 180),
        parent=camera.ui,
    )
    game.nft_text = Text(
        text="NFT Envanteri:",
        position=(-0.6, 0.13),
        color=color.white,
        parent=camera.ui,
    )
    game.nft_button = Button(
        text="Demo NFT Mintle",
        position=(-0.6, 0.10),
        color=color.azure,
        parent=camera.ui,
        on_click=lambda: game.nft_text.set_text(f"NFT Envanteri: {game.demo.mint_demo_nft()['name']}")
    )
    # AI NPC panel
    game.npc_panel = Entity(
        model='quad',
        scale=Vec3(0.2, 0.10, 1),
        position=Vec3(-0.6, 0.02, 0),
        color=color.rgba(0, 212, 255, 180),
        parent=camera.ui,
    )
    game.npc_text = Text(
        text=f"NPC Kararları: {game.demo.npc_decisions(120, 15)}",
        position=(-0.6, 0.03),
        color=color.white,
        parent=camera.ui,
    )
    # Dünya paneli
    game.world_panel = Entity(
        model='quad',
        scale=Vec3(0.2, 0.10, 1),
        position=Vec3(-0.6, -0.08, 0),
        color=color.rgba(0, 212, 255, 180),
        parent=camera.ui,
    )
    game.world_text = Text(
        text=f"Dünya Haritası: {len(game.demo.get_world_map())} tile",
        position=(-0.6, -0.07),
        color=color.white,
        parent=camera.ui,
    )
    # Temizlik için ekle
    game.ui_elements['demo'] = [
        game.vr_panel, game.vr_text, game.vr_button,
        game.nft_panel, game.nft_text, game.nft_button,
        game.npc_panel, game.npc_text,
        game.world_panel, game.world_text
    ]
