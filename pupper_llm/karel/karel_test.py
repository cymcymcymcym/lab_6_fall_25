# karel_test.py

import karel


def main():
    pupper = karel.KarelPupper()
    pupper.wiggle()
    pupper.move_forward()
    pupper.turn_right()
    pupper.move_backward()
    pupper.turn_right()
    pupper.move_left()
    pupper.turn_right()
    pupper.move_right()
    pupper.turn_right()
    

if __name__ == '__main__':
    main()
