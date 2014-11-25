"""
test.test_component_sun
~~~~~~~~~~~~~~~~~~~~~~~

Tests Sun component.
"""
# pylint: disable=too-many-public-methods,protected-access
import unittest
import datetime as dt

import ephem

import homeassistant as ha
import homeassistant.components.sun as sun


class TestSun(unittest.TestCase):
    """ Test the sun module. """

    def setUp(self):  # pylint: disable=invalid-name
        self.hass = ha.HomeAssistant()

    def tearDown(self):  # pylint: disable=invalid-name
        """ Stop down stuff we started. """
        self.hass._pool.stop()

    def test_is_on(self):
        """ Test is_on method. """
        self.hass.states.set(sun.ENTITY_ID, sun.STATE_ABOVE_HORIZON)
        self.assertTrue(sun.is_on(self.hass))
        self.hass.states.set(sun.ENTITY_ID, sun.STATE_BELOW_HORIZON)
        self.assertFalse(sun.is_on(self.hass))

    def test_setting_rising(self):
        """ Test retrieving sun setting and rising. """
        # Compare it with the real data
        self.assertTrue(sun.setup(
            self.hass,
            {ha.DOMAIN: {
                ha.CONF_LATITUDE: '32.87336',
                ha.CONF_LONGITUDE: '117.22743'
            }}))

        observer = ephem.Observer()
        observer.lat = '32.87336'  # pylint: disable=assigning-non-slot
        observer.long = '117.22743'  # pylint: disable=assigning-non-slot

        body_sun = ephem.Sun()  # pylint: disable=no-member
        next_rising_dt = ephem.localtime(observer.next_rising(body_sun))
        next_setting_dt = ephem.localtime(observer.next_setting(body_sun))

        # Home Assistant strips out microseconds
        # strip it out of the datetime objects
        next_rising_dt = next_rising_dt - dt.timedelta(
            microseconds=next_rising_dt.microsecond)
        next_setting_dt = next_setting_dt - dt.timedelta(
            microseconds=next_setting_dt.microsecond)

        self.assertEqual(next_rising_dt, sun.next_rising(self.hass))
        self.assertEqual(next_setting_dt, sun.next_setting(self.hass))

        # Point it at a state without the proper attributes
        self.hass.states.set(sun.ENTITY_ID, sun.STATE_ABOVE_HORIZON)
        self.assertIsNone(sun.next_rising(self.hass))
        self.assertIsNone(sun.next_setting(self.hass))

        # Point it at a non-existing state
        self.assertIsNone(sun.next_rising(self.hass, 'non.existing'))
        self.assertIsNone(sun.next_setting(self.hass, 'non.existing'))

    def test_setup(self):
        """ Test Sun setup with empty and wrong configs. """
        self.assertFalse(sun.setup(self.hass, {}))
        self.assertFalse(sun.setup(self.hass, {sun.DOMAIN: {}}))
        self.assertFalse(sun.setup(
            self.hass, {ha.DOMAIN: {ha.CONF_LATITUDE: '32.87336'}}))
        self.assertFalse(sun.setup(
            self.hass, {ha.DOMAIN: {ha.CONF_LONGITUDE: '117.22743'}}))
        self.assertFalse(sun.setup(
            self.hass, {ha.DOMAIN: {ha.CONF_LATITUDE: 'hello'}}))
        self.assertFalse(sun.setup(
            self.hass, {ha.DOMAIN: {ha.CONF_LONGITUDE: 'how are you'}}))
        self.assertFalse(sun.setup(
            self.hass, {ha.DOMAIN: {
                ha.CONF_LATITUDE: 'wrong', ha.CONF_LONGITUDE: '117.22743'
            }}))
        self.assertFalse(sun.setup(
            self.hass, {ha.DOMAIN: {
                ha.CONF_LATITUDE: '32.87336', ha.CONF_LONGITUDE: 'wrong'
            }}))

        # Test with correct config
        self.assertTrue(sun.setup(
            self.hass, {ha.DOMAIN: {
                ha.CONF_LATITUDE: '32.87336', ha.CONF_LONGITUDE: '117.22743'
            }}))
