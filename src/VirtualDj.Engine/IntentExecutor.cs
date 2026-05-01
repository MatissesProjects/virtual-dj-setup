namespace VirtualDj.Engine
{
    public class IntentExecutor
    {
        private readonly DspPipeline _pipeline;
        private readonly MasterMixer _mixer;

        public IntentExecutor(DspPipeline pipeline, MasterMixer mixer)
        {
            _pipeline = pipeline;
            _mixer = mixer;
        }

        public void Execute(IntentType intent)
        {
            if (_pipeline.Authority == ControlAuthority.Human)
            {
                // Silent yield - we don't apply AI intents while human is in control
                return;
            }

            switch (intent)
            {
                case IntentType.CreateTension:
                    // Use smooth automation instead of hard jump
                    _pipeline.AutomateWidth(2.5f, 4000, 44100); // 4 second fade
                    _pipeline.CompressionRatio = 8.0f;
                    break;

                case IntentType.ExecuteDrop:
                    // Reset to punchy settings
                    _pipeline.Width = 1.1f;
                    _pipeline.CompressionRatio = 2.0f;
                    Console.WriteLine("[MACRO] Drop executed: Resetting stereo and dynamics for punch.");
                    break;

                case IntentType.SmoothBlend:
                    // Toggle crossfader over 8 seconds (8000ms)
                    float target = _mixer.Crossfader.Position < 0.5f ? 1.0f : 0.0f;
                    _mixer.Crossfader.Automate(target, 8000, 44100);
                    Console.WriteLine($"[MACRO] Smooth Blend: Fading to {target} over 8 seconds.");
                    break;

                case IntentType.GenerateBridge:
                    // Fade in the bridge additive layer
                    _mixer.BridgeLevel = 1.0f;
                    Console.WriteLine("[MACRO] Generative Bridge Active: Fading in AI Synthesis.");
                    break;

                case IntentType.Idle:
                    _pipeline.Width = 1.2f;
                    _pipeline.CompressionRatio = 2.0f;
                    break;
            }
        }
    }
}
