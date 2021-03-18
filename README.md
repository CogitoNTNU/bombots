[![Build Status](https://travis-ci.org/CogitoNTNU/bombots.svg?branch=main)](https://travis-ci.org/CogitoNTNU/bombots)

# Bombots 💣🤖
AI Tournament Environment, inspired by Pommerman. Created for the Cogito NTNU AI Competition spring semester 2021.

# Setup
To setup the system on your machine, clone the repository, install dependencies, and make sure the test file runs properly. The test file should launch an environment with some example agents that play against each other until you close the window.
```
git clone https://github.com/CogitoNTNU/bombots.git
cd bombots
pip install -r requirements.txt
python main.py
```
After confirming that everything works fine, you can move on to developing you own agent. A good starting point for this is to take a look at [the agent template](agent_template.py) code and how it's used in [the example](main.py). The next step is to change the act-function in the agent and write your own AI code. Feel free to follow another design pattern if you prefer so, but for the competition we will eventually announce a specific layout that is in compliance with the tournament engine.
# Cogito NTNU AI Competition
For students at NTNU, see the [official competition page](https://s.ntnu.no/bombots) for information about rules, submission, tips etc.

# Planned updates
- [ ] OpenAI gym support (for standardized reinforcement learning)
- [ ] More example agents
- [ ] Replay recording and playback
- [ ] More metrics
- [ ] Support for distributed execution
