import React from 'react';

const SimulationResult = ({ result }) => {
    if (!result || !result.data) return null;

    const { current_approval_probability, missing_evidence, scenarios } = result.data;

    // Determine color based on probability
    const getScoreColor = (score) => {
        if (score >= 80) return '#4ade80'; // Green
        if (score >= 50) return '#facc15'; // Yellow
        return '#f87171'; // Red
    };

    return (
        <div className="analysis-result-container" style={{ padding: '20px', backgroundColor: 'rgba(30, 41, 59, 0.7)', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <h3 style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '10px', marginBottom: '20px' }}>
                🔮 Claim Outcome Simulation
            </h3>

            {/* Probability Gauge */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '30px' }}>
                <div style={{
                    position: 'relative',
                    width: '120px',
                    height: '120px',
                    borderRadius: '50%',
                    background: `conic-gradient(${getScoreColor(current_approval_probability)} ${current_approval_probability}%, rgba(255,255,255,0.1) 0)`
                }}>
                    <div style={{
                        position: 'absolute',
                        top: '10px',
                        left: '10px',
                        right: '10px',
                        bottom: '10px',
                        backgroundColor: '#0f172a',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexDirection: 'column'
                    }}>
                        <span style={{ fontSize: '28px', fontWeight: 'bold', color: 'white' }}>{current_approval_probability}%</span>
                        <span style={{ fontSize: '10px', color: '#94a3b8' }}>APPROVAL CHANCE</span>
                    </div>
                </div>
            </div>

            {/* Missing Evidence */}
            {missing_evidence && missing_evidence.length > 0 && (
                <div style={{ marginBottom: '20px' }}>
                    <h4 style={{ color: '#f87171', marginBottom: '10px' }}>⚠️ Missing Critical Evidence</h4>
                    <ul style={{ paddingLeft: '20px', color: '#cbd5e1' }}>
                        {missing_evidence.map((item, idx) => (
                            <li key={idx} style={{ marginBottom: '5px' }}>{item}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Scenarios */}
            <div>
                <h4 style={{ color: '#60a5fa', marginBottom: '15px' }}>📈 How to Improve Your Odds</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {scenarios.map((scenario, idx) => (
                        <div key={idx} style={{
                            padding: '12px',
                            borderRadius: '8px',
                            backgroundColor: 'rgba(255,255,255,0.05)',
                            borderLeft: `4px solid ${getScoreColor(scenario.estimated_probability)}`
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                                <strong style={{ color: 'white' }}>Scenario {idx + 1}</strong>
                                <span style={{
                                    fontWeight: 'bold',
                                    color: getScoreColor(scenario.estimated_probability)
                                }}>
                                    → {scenario.estimated_probability}%
                                </span>
                            </div>
                            <p style={{ margin: 0, fontSize: '0.9em', color: '#cbd5e1' }}>{scenario.description}</p>
                            <p style={{ margin: '5px 0 0 0', fontSize: '0.8em', color: '#94a3b8', fontStyle: 'italic' }}>
                                "{scenario.reasoning}"
                            </p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default SimulationResult;
