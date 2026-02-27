# ELoRa: An end-to-end LoRaWAN emulator for the ChirpStack network server #

This is a traffic emulator for the [Chirpstack server stack](https://www.chirpstack.io/ "ChirpStack, open-source LoRaWAN® Network Server").

This software can be used to simulate in real-time multiple devices and gateways sharing a radio channel with very high flexibility in terms of possible configurations. LoRaWAN traffic is then UDP-encapsulated by gateways and forwarded outside the simulation. If a Chirpstack network server is in place, it will think the traffic is coming from a real network. All Class A MAC primitives used in the UE868 region are supported: radio transmission parameters of simulated devices can be changed by the downlink LoRaWAN traffic of the real server.

In this repository we provide a quick installation using Docker Compose. If you are interested to the emulation internal working and developement we refer you to the [emulator code repository](https://github.com/Orange-OpenSource/elora).

ELoRa was developed by extending the [LoRaWAN module](https://github.com/signetlabdei/lorawan "LoRaWAN ns-3 module") of the [ns-3](https://gitlab.com/nsnam/ns-3-dev "The Network Simulator, Version 3") network simulator.

## Prerequisites ##

To use the emulator you need to do/know the following:

* Your host system must to be running Linux and [Docker Compose](https://docs.docker.com/compose/) must to be installed on your system
* The [ChirpStack server infrastructure](https://www.chirpstack.io/docs/architecture.html) must to be running somewhere reachable by the host network
* The simulator works with ChirpStark v4. It has been tested with a local [docker-compose installation](https://www.chirpstack.io/docs/getting-started/docker.html "Chirpstack docs: Quickstart Docker Compose") of the server
* An authentification token needs to be generated in the server UI (API keys section), and needs to be placed in a dedicated `.env.chirpstack-api-token` new file at the root of this repo.
* If you have a distributed deployment of ChirpStack, you need to change the IP/port of the server's REST API endpoint in [`configuration.toml`](/configuration.toml), as well as the IP/port of the ChirpStack Gateway Bridge

## Usage ##

After cloning into this repository, the emulator can be run with Docker Compose:

```sh
git clone https://github.com/nondetalle/elora-docker.git
cd elora-docker
docker compose up
```

Inside [`elora-example/`](/elora-example/) we provide an example scenario. Numerical parameters exposed by this example can be changed in [`configuration.toml`](/configuration.toml) before running the emulation. You can directly change the exposed parameters, or create an entirely new scenario, by editing the main ns-3 file [`elora-example.cc`](/elora-example/elora-example.cc). All this can be done without re-building the module; scenario files are loaded and built at runtime by Docker Compose.

If you want to go a step further, and change the internal ns-3 libraries, you can add your own module repository in the [`build/`](/build/) directory, edit the [`Dockerfile`](/build/Dockerfile) accordingly, and run `docker compose build` from the root directory of this repository. Make sure you [init the ns-3 submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) in the [`build/`](/build/) directory.

We support the developement philosophy of ns-3. Feel free to contribute by forking [the module repository](https://github.com/Orange-OpenSource/elora).

For more information on how to use the underlying LoRaWAN module refer to the [original module readme](https://github.com/signetlabdei/lorawan/blob/e8f7a21044418e92759d5c7c4bcab147cdaf05b3/README.md "LoRaWAN ns-3 module README").

## Getting help ##

If you need any help, feel free to open an issue here or on the [module repository](https://github.com/Orange-OpenSource/elora).

## Cite us ##

[A. Aimi, S. Rovedakis, F. Guillemin, and S. Secci, “ELoRa: End-to-end Emulation of Massive IoT LoRaWAN Infrastructures,” 2023 IEEE/IFIP Network Operations and Management Symposium (NOMS), May 2023, Miami, FL, United States.](https://hal.science/hal-04025834)
