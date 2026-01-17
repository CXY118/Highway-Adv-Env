# Highway-Adv-Env
在 highway-env 中构建对抗性测试场景/Building Adversarial Test Scenarios in highway-env
## Prerequisites
Python 3.8+; Ensure 'pip' or 'conda' is available;<br>
pip install pandas numpy or conda install pandas numpy highwayenv
## File Contents
### FSM cut_in
FSM_based_cut_in_vehicle.py (An adversarial vehicle controller using finite-state machine for cut-in maneuvers)<br>
FSM_based_cut_in_environment.py (Construction of an Adversarial Cut-in Environment Based on Finite State Machine)<br>
data_recorder.py (A data recording tool used to capture vehicle interaction data during cut-in events)<br>
plotter.py (A visualization tool that renders vehicle trajectories)<br>
test_FSM_based_cut_in_vehicle.py (Adversarial Vehicle Control Framework Utilizing Finite State Machine)<br>
data_analyze_example.py (plotting example)
#### FSM
<img width=50% alt="FSM" src="https://github.com/user-attachments/assets/8f8add85-ea36-4f2c-9d08-36020ce15085" />

#### Demo Video
[![FSM cutin](https://github.com/user-attachments/assets/5af99b08-a519-4046-bc0e-268595cc7d5d)](https://github.com/user-attachments/assets/5af99b08-a519-4046-bc0e-268595cc7d5d){: width="50%"}
#### Plotting Example
<img width=50% alt="Figure_1" src="https://github.com/user-attachments/assets/f1f73e40-808e-4e8e-936d-22d75b6217c7" />
