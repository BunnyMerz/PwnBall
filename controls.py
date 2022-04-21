class PlayerControls:
    controls = []
    def __init__(self, player, rules):
        self.player = player
        self.rules = rules # {'move_left': K_a}

        PlayerControls.controls.append(self)

    def main(keys_pressed):
        for c in PlayerControls.controls:
            c.main_(keys_pressed)

    def main_(self,keys_pressed):

        movement = {'left': keys_pressed[self.rules['move_left']],
        'right': keys_pressed[self.rules['move_right']],
        'up': keys_pressed[self.rules['move_up']],
        'down': keys_pressed[self.rules['move_down']],
        'speed': ['normal','fast'][keys_pressed[self.rules['speed_up']]]}

        self.player.move(movement)
