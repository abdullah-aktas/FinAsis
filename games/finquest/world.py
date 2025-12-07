# -*- coding: utf-8 -*-
"""
World building helpers for FinQuest 3D.

These functions operate on the game instance (passed as `game`) and are
responsible for constructing the tutorial world, the main city center, and the
overall game world composition. UI/HUD elements remain in the game class for
now and can be modularized separately.
"""

from ursina import Entity, Sky, Text, Button, camera, color, Func, Vec3
from ursina.prefabs.first_person_controller import FirstPersonController
import random


def create_tutorial_world(game):
    """Build the tutorial world on the provided game instance."""
    # Sky
    game.sky = Sky()

    # Ground
    game.ground = Entity(
        model="plane",
        scale=Vec3(100, 1, 100),
        color=color.green,
        texture="grass",
        collider="box",
    )

    # Walls
    game.walls = [
        Entity(
            model="cube",
            scale=Vec3(1, 5, 100),
            position=Vec3(-50, 2.5, 0),
            color=color.gray,
            texture="brick",
            collider="box",
        ),
        Entity(
            model="cube",
            scale=Vec3(1, 5, 100),
            position=Vec3(50, 2.5, 0),
            color=color.gray,
            texture="brick",
            collider="box",
        ),
        Entity(
            model="cube",
            scale=Vec3(100, 5, 1),
            position=Vec3(0, 2.5, 50),
            color=color.gray,
            texture="brick",
            collider="box",
        ),
        Entity(
            model="cube",
            scale=Vec3(100, 5, 1),
            position=Vec3(0, 2.5, -50),
            color=color.gray,
            texture="brick",
            collider="box",
        ),
    ]

    # Tutorial buildings
    game.tutorial_buildings = [
        Entity(
            model="cube",
            scale=Vec3(10, 5, 10),
            position=Vec3(20, 2.5, 20),
            color=color.azure,
            texture="brick",
            collider="box",
        ),
        Entity(
            model="cube",
            scale=Vec3(10, 7, 10),
            position=Vec3(-20, 3.5, -20),
            color=color.orange,
            texture="brick",
            collider="box",
        ),
        Entity(
            model="cube",
            scale=Vec3(10, 4, 10),
            position=Vec3(20, 2, -20),
            color=color.green,
            texture="brick",
            collider="box",
        ),
        Entity(
            model="cube",
            scale=Vec3(10, 6, 10),
            position=Vec3(-20, 3, 20),
            color=color.yellow,
            texture="brick",
            collider="box",
        ),
    ]

    # Building signs
    game.building_signs = [
        Entity(
            text="MARKET",
            scale=Vec3(2, 2, 2),
            position=Vec3(20, 6, 20),
            color=color.blue,
            billboard=True,
        ),
        Entity(
            text="BANKA",
            scale=Vec3(2, 2, 2),
            position=Vec3(-20, 8, -20),
            color=color.gold,
            billboard=True,
        ),
        Entity(
            text="OFİS",
            scale=Vec3(2, 2, 2),
            position=Vec3(20, 5, -20),
            color=color.lime,
            billboard=True,
        ),
        Entity(
            text="EĞİTİM MERKEZİ",
            scale=Vec3(2, 2, 2),
            position=Vec3(-20, 6.5, 20),
            color=color.red,
            billboard=True,
        ),
    ]

    # Player controller
    game.player_controller = FirstPersonController(position=Vec3(0, 1, 0), speed=10)

    # Tutorial overlay panel
    Entity(
        model="quad",
        scale=Vec3(0.6, 0.3, 1),
        position=Vec3(0, 0.3, 0),
        color=color.rgba(0, 0, 0, 0.8),
        parent=camera.ui,
    )

    Text(
        text="Ticaretin İzinde - Eğitim Modu",
        scale=2,
        position=Vec3(0, 0.4, 0),
        origin=(0, 0),
        color=color.yellow,
        parent=camera.ui,
    )

    Text(
        text="Etrafınızdaki binaları ziyaret ederek ticaret dünyasını öğrenin.\nMarkette alım-satım yapın, bankada kredi çekin, ofiste işletmenizi yönetin.",
        scale=1.2,
        position=Vec3(0, 0.3, 0),
        origin=(0, 0),
        color=color.white,
        parent=camera.ui,
    )

    # Skip tutorial button
    Button(
        text="Eğitimi Atla",
        scale=Vec3(0.2, 0.05, 1),
        position=Vec3(0, 0.2, 0),
        parent=camera.ui,
        on_click=Func(game.complete_tutorial),
    )

    # Cache in world_elements
    game.world_elements = {
        "sky": game.sky,
        "ground": game.ground,
        "walls": game.walls,
        "buildings": game.tutorial_buildings,
        "signs": game.building_signs,
        "player": game.player_controller,
    }


def create_city_center(game):
    """Create the main city center with roads, buildings, triggers and decorations."""
    # Roads
    roads = [
        Entity(
            model="cube",
            scale=Vec3(100, 0.1, 10),
            position=Vec3(0, 0.05, 0),
            color=color.gray,
            texture="asphalt",
        ),
        Entity(
            model="cube",
            scale=Vec3(10, 0.1, 100),
            position=Vec3(0, 0.05, 0),
            color=color.gray,
            texture="asphalt",
        ),
    ]

    # Buildings specification
    buildings = []
    building_positions = [
        {
            "position": (20, 0, 20),
            "scale": (15, 10, 15),
            "color": color.azure,
            "name": "MARKET",
            "type": "market",
        },
        {
            "position": (-20, 0, -20),
            "scale": (15, 12, 15),
            "color": color.gold,
            "name": "BANKA",
            "type": "bank",
        },
        {
            "position": (20, 0, -20),
            "scale": (15, 8, 15),
            "color": color.green,
            "name": "OFİS",
            "type": "office",
        },
        {
            "position": (-20, 0, 20),
            "scale": (15, 14, 15),
            "color": color.orange,
            "name": "EĞİTİM MERKEZİ",
            "type": "education",
        },
    ]

    # Build each building with door, sign, entry point and trigger
    for building_data in building_positions:
        building = Entity(
            model="cube",
            position=Vec3(
                building_data["position"][0],
                building_data["scale"][1] / 2,
                building_data["position"][2],
            ),
            scale=Vec3(*building_data["scale"]),
            color=building_data["color"],
            texture="brick",
            collider="box",
        )

        sign = Entity(
            model="billboard",
            parent=building,
            position=Vec3(0, building_data["scale"][1] / 2 + 1, 0),
            scale=Vec3(3, 3, 3),
            color=color.white,
            billboard=True,
        )

        Text(
            text=building_data["name"],
            parent=sign,
            scale=10,
            origin=(0, 0),
            color=color.black,
        )

        door = Entity(
            model="cube",
            parent=building,
            position=Vec3(
                0,
                -building_data["scale"][1] / 2 + 1,
                building_data["scale"][2] / 2 + 0.1,
            ),
            scale=Vec3(3, 5, 0.2),
            color=color.brown,
            collider="box",
        )

        entry_point = Entity(
            model="sphere",
            parent=building,
            position=Vec3(
                0, -building_data["scale"][1] / 2 + 1, building_data["scale"][2] / 2 + 2
            ),
            scale=Vec3(0.5, 0.5, 0.5),
            color=color.black,
            visible=False,
        )
        entry_point.building_type = building_data["type"]

        trigger = Entity(
            parent=building,
            position=Vec3(
                0, -building_data["scale"][1] / 2 + 1, building_data["scale"][2] / 2 + 3
            ),
            scale=Vec3(5, 5, 5),
            collider="box",
            visible=False,
        )
        trigger.building_type = building_data["type"]

        # Interaction callbacks
        def on_trigger_enter(trigger=trigger):
            game.interaction_target = trigger.building_type
            game.show_interaction_prompt(
                f"'{trigger.building_type.capitalize()}' binasına girmek için E tuşuna basın"
            )

        def on_trigger_exit(trigger=trigger):
            if game.interaction_target == trigger.building_type:
                game.interaction_target = None
                game.hide_interaction_prompt()

        # In this simplified approach, use click to simulate trigger enter
        trigger.on_click = Func(on_trigger_enter)

        buildings.append(
            {
                "entity": building,
                "sign": sign,
                "door": door,
                "entry_point": entry_point,
                "trigger": trigger,
                "type": building_data["type"],
            }
        )

    # Decorations
    decorations = []

    # Trees
    for _ in range(50):
        x = random.uniform(-100, 100)
        z = random.uniform(-100, 100)

        too_close = False
        for b in buildings:
            bx, _, bz = b["entity"].position
            if abs(x - bx) < 20 and abs(z - bz) < 20:
                too_close = True
                break

        if not too_close:
            tree = Entity(
                model="cube",
                position=Vec3(x, 2, z),
                scale=Vec3(1, 4, 1),
                color=color.brown,
            )
            leaves = Entity(
                model="sphere",
                parent=tree,
                position=Vec3(0, 2, 0),
                scale=Vec3(3, 3, 3),
                color=color.green,
            )
            decorations.append((tree, leaves))

    # Benches
    for _ in range(10):
        x = random.uniform(-50, 50)
        z = random.uniform(-50, 50)
        bench = Entity(
            model="cube",
            position=Vec3(x, 0.5, z),
            scale=Vec3(2, 0.5, 0.5),
            color=color.brown,
        )
        decorations.append(bench)

    # Save to world elements (partial; other keys are set by create_game_world)
    game.world_elements.update(
        {
            "roads": roads,
            "buildings": buildings,
            "decorations": decorations,
        }
    )


def create_game_world(game):
    """Build the main game world: sky, ground, city center, player, and then UI via game method."""
    game.current_screen = "game"

    # Sky and ground
    game.sky = Sky()
    game.ground = Entity(
        model="plane",
        scale=Vec3(1000, 1, 1000),
        color=color.green,
        texture="grass",
        collider="box",
    )

    # Initialize world_elements cache
    game.world_elements = {
        "sky": game.sky,
        "ground": game.ground,
    }

    # City center
    create_city_center(game)

    # Player
    game.player_controller = FirstPersonController(position=Vec3(0, 2, 0), speed=10)
    game.world_elements["player"] = game.player_controller

    # Create UI and assign default quests through the game class API
    # (UI modularization will be handled in finquest.ui in a later step.)
    if hasattr(game, "create_game_ui"):
        game.create_game_ui()
    if hasattr(game, "assign_default_quests"):
        game.assign_default_quests()
