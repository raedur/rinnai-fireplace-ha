# HACS Module for LS Series Rinnai Fireplaces

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]

_Integration to integrate with [rinnai_fireplace][rinnai_fireplace]._

**This integration will set up the following platforms.**

Platform | Description
-- | --
`climate` | Climate entity for the Rinnai Fireplace.

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `rinnai_fireplace`.
1. Download _all_ the files from the `custom_components/rinnai_fireplace/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Integration blueprint"

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[rinnai_fireplace]: https://github.com/raedur/rinnai-fireplace-ha
[buymecoffee]: https://www.buymeacoffee.com/ludeeus
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/raedur/rinnai-fireplace-ha.svg?style=for-the-badge
[commits]: https://github.com/raedur/rinnai-fireplace-ha/commits/main
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/raedur/rinnai-fireplace-ha.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Raedur-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/raedur/rinnai-fireplace-ha.svg?style=for-the-badge
[releases]: https://github.com/raedur/rinnai-fireplace-ha/releases
