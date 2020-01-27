import matplotlib.pyplot as plt
import math, numpy


def degTOstep(deg):
    return deg * 200 * 16 / 360


def move_chirp(amplitude, frequency, duration):

    beta = float(frequency) / float(duration)
    a_s = int(degTOstep(amplitude))
    divisions = 5000
    t = numpy.linspace(0, 1, divisions)
    phase = 2 * numpy.pi * (0.5 * beta * t * t)
    disp = [0.0] * divisions
    for i in range(0, divisions):disp[i] = amplitude * math.sin(phase[i])
    plt.plot(t, disp)
    plt.show()

if __name__ == "__main__":

    move_chirp(30, 2000, 10)
