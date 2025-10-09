# 🎮 Audio-Controlled Car Games Collection

This collection contains several voice-controlled driving games with different features and visual styles.

## 🚗 Game Versions

### 1. **Original Audio Driving Game** (`audio_driving_game.py`)
- **Features**: Dual-panel layout with audio visualization
- **Controls**: Low frequency sounds → LEFT, High frequency sounds → RIGHT
- **Graphics**: Chart-based with matplotlib plots
- **Audience**: Technical users who want to see audio analysis

### 2. **Cartoon Car Game** (`cartoon_car_game.py`)
- **Features**: Pure visual game with cartoon-style graphics
- **Controls**: LOUD voice → LEFT, QUIET voice → RIGHT
- **Graphics**: Colorful cartoon cars, trees, clouds, animated road
- **Audience**: Casual gamers who want simple, fun visuals

### 3. **Enhanced Car Game** (`enhanced_car_game.py`)
- **Features**: Advanced cartoon graphics with scenery and animations
- **Controls**: LOUD voice → LEFT, QUIET voice → RIGHT  
- **Graphics**: Detailed cars, grass, trees, flowers, smooth animations
- **Audience**: Players who want the best visual experience

## 🎵 How Audio Control Works

All games use your microphone to control the car:

### Simple Volume Control (Recommended)
- **LOUD sounds** (shouting, clapping, music) → Move LEFT
- **QUIET/SILENT** → Move RIGHT
- **Medium sounds** → Stay centered

### Frequency Analysis Control (Original game)
- **Low frequency sounds** (humming "mmm", bass sounds) → Move LEFT
- **High frequency sounds** (whistling "eee", high pitch) → Move RIGHT

## 🕹️ Game Objective

- Drive your red car down the road
- Avoid hitting the obstacle cars (blue/colored cars)
- Score points by surviving longer
- Game gets faster as your score increases
- Try to beat your high score!

## 🚀 How to Play

```bash
cd /Users/tanpujiahui/Interactive_Experience_Assignment3
source .venv/bin/activate

# Choose your preferred game:
python week06/cartoon_car_game.py        # Simple cartoon version
python week06/enhanced_car_game.py       # Advanced graphics version  
python week06/audio_driving_game.py      # Original with audio charts
```

## 🎯 Tips for Best Experience

1. **Microphone Setup**: Make sure your microphone is working and positioned well
2. **Sound Control**: Practice making loud and quiet sounds consistently
3. **Environment**: Play in a quiet room for better audio detection
4. **Audio Levels**: The games auto-adjust to your microphone sensitivity
5. **Practice**: Start with short sounds to get used to the controls

## 🛠️ Technical Features

- **Real-time audio processing** using PyAudio
- **Smooth graphics** with matplotlib animations
- **Collision detection** between cars
- **Dynamic difficulty** that increases with score
- **Cross-platform** compatibility (Windows, macOS, Linux)
- **No additional hardware** required (just a microphone)

## 🎨 Visual Differences

| Feature | Original | Cartoon | Enhanced |
|---------|----------|---------|----------|
| Audio Chart | ✅ Yes | ❌ No | ❌ No |
| Road Animation | Basic | Good | Excellent |
| Car Graphics | Simple | Cartoon | Detailed |
| Scenery | Minimal | Trees/Clouds | Trees/Flowers/Grass |
| UI Design | Technical | Fun | Polished |
| Performance | Medium | Fast | Fast |

## 🔧 Customization Options

You can easily modify these games:

- **Change car colors**: Edit the `colors` dictionary
- **Adjust sensitivity**: Modify `movement_sensitivity` and `volume_threshold`
- **Add new obstacles**: Create new shapes in the obstacle functions
- **Change difficulty**: Adjust `game_speed` progression
- **Add sound effects**: Integrate with pygame for audio feedback

## 🐛 Troubleshooting

**No audio input detected:**
- Check microphone permissions
- Try different audio devices
- Adjust system audio settings

**Game runs slowly:**
- Close other applications
- Reduce animation interval in FuncAnimation
- Use the simpler cartoon version

**Controls not responsive:**
- Speak louder or closer to microphone
- Check microphone levels in system settings
- Try different types of sounds (clapping, whistling, etc.)

## 🏆 High Score Challenge

Try to beat these milestones:
- 🥉 **Bronze**: Score 500+ points
- 🥈 **Silver**: Score 1000+ points  
- 🥇 **Gold**: Score 2000+ points
- 💎 **Diamond**: Score 5000+ points

Have fun playing! 🎉