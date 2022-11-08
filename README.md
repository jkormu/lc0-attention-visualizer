# lc0-attention-visualizer (WIP)
Visualizes attention layer activations of lc0 attention body nets as heatmaps.

## Quick start using conda env (untested)
1. Clone this repo:
 ```
    git clone https://github.com/jkormu/lc0-attention-visualizer.git lc0-attention-visualizer
    cd lc0-attention-visualizer
```
2. Create conda environment and install dependencies for lczero-training and attention visualizer:
```
conda create -n attention-viz python=3.8
conda activate attention-viz
conda install -c anaconda cudatoolkit

pip install tensorflow==2.5
pip install protobuf==3.12.1
pip install tensorflow-addons==0.18.0
pip install pyyaml==6.0
pip install python-chess==1.999
pip install dash=2.6.2
```

3. Clone and setup attention-net-body branch of lczero-training:
```
git clone -b attention-net-body  https://github.com/jkormu/lczero-training.git lczero-training
cd lczero-training
sh init.sh
cd ..
```

4. Prepare model folder where visualizer can read attention models from:
   * Crate folder called `models`
   * place at least one model folder inside models folder that containts at least one attention body net and config.yaml 
   for that net architecture
   * In the end folder structure could look like
   ```
   lc0-attention-visualizer/
        models/
            architecture1/
                cfg.yaml
                BT1024-3142c-swa-186000.pb.gz
                BT1024-rl-lowlr-swa-236500.pb.gz
            architecture2/
                cfg.yaml
                modelxxx.pb.gz
        run.py
        ...
    ```

5. Run the gui
```
python run.py
```

GUI should soon launch in your default browser.