# Veripeditus Game Server

Server component for the Veripeditus game framework

## What is Veripeditus?

Veripeditus (from Latin „veritas“ → „truth“ and „pedis“ → „foot“) is a
client/server augmented reality gaming engine and framework. It allows
writing game „cartridges“ for the server, which it can then run. Players
access the game while being outside with a mobile device.

## Development

The server component, the framework and the games are developed in pure
Python. There are a few design/development principals:

 * Game cartridges must be easy to develop with basic Python skills
 * The framework and engine must be dynamic enough to allow a large
   number of different game types to be developed
 * The framework must not carry any code that is specific to only
   a single type of game
 * Development is test-driven and test-first
 * pylint is to be used and obeyed

[![Build Status](https://travis-ci.org/Veripeditus/veripeditus-server.svg?branch=master)](https://travis-ci.org/Veripeditus/veripeditus-server)
