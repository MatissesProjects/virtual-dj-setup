namespace VirtualDj.Engine
{
    public class IntentExecutor
    {
        private readonly DspPipeline _pipeline;

        public IntentExecutor(DspPipeline pipeline)
        {
            _pipeline = pipeline;
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
                    // Increase width and ratio, maybe add make-up gain
                    _pipeline.Width = 2.0f; 
                    _pipeline.CompressionRatio = 8.0f;
                    Console.WriteLine("[MACRO] Tension building: Widening stereo and increasing compression.");
                    break;

                case IntentType.ExecuteDrop:
                    // Reset to punchy settings
                    _pipeline.Width = 1.1f;
                    _pipeline.CompressionRatio = 2.0f;
                    Console.WriteLine("[MACRO] Drop executed: Resetting stereo and dynamics for punch.");
                    break;

                case IntentType.Idle:
                    _pipeline.Width = 1.2f;
                    _pipeline.CompressionRatio = 2.0f;
                    break;
            }
        }
    }
}
