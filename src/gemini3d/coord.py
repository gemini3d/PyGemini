import numpy as np
import typing as T
import math

pi = math.pi


def geomag2geog(thetat: np.ndarray, phit: np.ndarray) -> T.Tuple[np.ndarray, np.ndarray]:
    """ geomagnetic to geographic """

    # FIXME: this is for year 1985, see Schmidt spherical harmonic in MatGemini
    thetan = math.radians(11)
    phin = math.radians(289)

    phit = np.atleast_1d(phit)

    # enforce phit = [0,2pi]
    i = phit > 2 * pi
    phitcorrected = phit
    phitcorrected[i] = phit[i] - 2 * pi
    i = phit < 0
    phitcorrected[i] = phit[i] + 2 * pi

    # thetag2p=acos(cos(thetat).*cos(thetan)-sin(thetat).*sin(thetan).*cos(phit));
    thetag2p = np.arccos(
        np.cos(thetat) * np.cos(thetan) - np.sin(thetat) * np.sin(thetan) * np.cos(phitcorrected)
    )

    beta = np.arccos(
        (np.cos(thetat) - np.cos(thetag2p) * np.cos(thetan)) / (np.sin(thetag2p) * np.sin(thetan))
    )

    phig2 = np.zeros_like(phitcorrected)

    i = phitcorrected > pi
    phig2[i] = phin - beta[i]

    i = phitcorrected <= pi
    phig2[i] = phin + beta[i]

    i = phig2 < 0
    phig2[i] = phig2[i] + 2 * pi

    i = phig2 >= 2 * pi
    phig2[i] = phig2[i] - 2 * pi

    thetag2 = pi / 2 - thetag2p
    lat = np.degrees(thetag2)
    lon = np.degrees(phig2)

    return lat, lon


def geog2geomag(lat: np.ndarray, lon: np.ndarray) -> T.Tuple[np.ndarray, np.ndarray]:
    """ geographic to geomagnetic """

    # FIXME: this is for year 1985, see Schmidt spherical harmonic in MatGemini
    thetan = math.radians(11)
    phin = math.radians(289)

    lat = np.atleast_1d(lat)
    lon = np.atleast_1d(lon)

    # enforce [0,360] longitude
    lon = lon % 360

    thetagp = pi / 2 - np.radians(lat)
    phig = np.radians(lon)

    thetat = np.arccos(
        np.cos(thetagp) * np.cos(thetan) + np.sin(thetagp) * np.sin(thetan) * np.cos(phig - phin)
    )
    argtmp = (np.cos(thetagp) - np.cos(thetat) * np.cos(thetan)) / (np.sin(thetat) * np.sin(thetan))
    alpha = np.arccos(max(min(argtmp, 1), -1))
    phit = np.empty(lat.shape)

    i = ((phin > phig) & ((phin - phig) > pi)) | ((phin < phig) & ((phig - phin) < pi))
    phit[i] = pi - alpha[i]
    phit[~i] = alpha[~i] + pi

    return thetat, phit


def geog2UEN(alt, glon, glat, thetactr, phictr):
    """
    Converts a set of glon,glat into magnetic up, north, east coordinates.
    thetactr and phictr are the magnetic coordinates of the center of hte region of interest.
    They can be computed from geog2geomag.
    """

    # %% UPWARD DISTANCE
    Re = 6370e3
    z = alt

    # Convert to geomganetic coordinates
    theta, phi = geog2geomag(glat, glon)

    # Convert to northward distance in meters
    gamma2 = theta - thetactr  # southward magnetic angular distance
    gamma2 = -gamma2  # convert to northward angular distance
    y = gamma2 * Re

    gamma1 = phi - phictr  # eastward angular distance
    x = Re * np.sin(thetactr) * gamma1

    return z, x, y


def UEN2geog(z, x, y, thetactr, phictr):
    """
    converts magnetic up, north, east coordinates into geographic coordinates.
    """

    # UPWARD DISTANCE
    Re = 6370e3
    alt = z

    # Northward angular distance
    gamma2 = y / Re  # must retain the sign of x3
    theta = thetactr - gamma2  # minus because distance north is against theta's direction

    # Eastward angular distance
    gamma1 = x / Re / np.sin(thetactr)
    # must retain the sign of x2, just use theta of center of grid
    phi = phictr + gamma1

    # Now convert the magnetic to geographic using our simple transformation
    [glat, glon] = geomag2geog(theta, phi)

    return alt, glon, glat
