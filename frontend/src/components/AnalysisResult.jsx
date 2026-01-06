import React from 'react';

const AnalysisResult = ({ result }) => {
    const [count, setCount] = React.useState(0);
    
    if (!result) return null;

    const { denial_risk_score, missing_requirements, reasoning_result, extracted_documents } = result;

    React.useEffect(() => {
        let start = 0;
        const duration = 2000; // 2 seconds
        const stepTime = 20;
        const steps = duration / stepTime;
        const increment = denial_risk_score / steps;
        
        const timer = setInterval(() => {
            start += increment;
            if (start >= denial_risk_score) {
                setCount(denial_risk_score);
                clearInterval(timer);
            } else {
                setCount(Math.floor(start));
            }
        }, stepTime);

        return () => clearInterval(timer);
    }, [denial_risk_score]);

    // Determine risk level
    const getRiskLevel = (score) => {
        if (score <= 30) return { level: 'low', label: 'Low Risk', class: 'risk-low' };
        if (score <= 70) return { level: 'medium', label: 'Medium Risk', class: 'risk-medium' };
        return { level: 'high', label: 'High Risk', class: 'risk-high' };
    };

    const risk = getRiskLevel(count);

    return (
        <div className="analysis-result">
            {/* Risk Score Display */}
            {denial_risk_score !== undefined && (
                <div className="risk-score-container fade-in">
                    <div className={`risk-score ${risk.class}`} style={{ transition: 'color 0.5s' }}>
                        {count}%
                    </div>
                    <div className={`risk-label ${risk.class}`}>
                        {risk.label}
                    </div>
                </div>
            )}

            {/* Extracted Documents Summary */}
            {extracted_documents && extracted_documents.length > 0 && (
                <div style={{ marginTop: '2rem' }}>
                    <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                        📋 Extracted Documents
                    </h3>
                    {extracted_documents.map((doc, index) => (
                        <div 
                            key={index} 
                            className="requirement-item stagger-enter" 
                            style={{ 
                                borderLeftColor: 'var(--primary-blue)',
                                animationDelay: `${index * 0.1}s` 
                            }}
                        >
                            <strong>{doc.type.replace('_', ' ').toUpperCase()}</strong>
                            <div style={{ fontSize: '0.875rem', marginTop: '0.5rem', color: 'var(--text-secondary)' }}>
                                {doc.filename}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Missing Requirements */}
            {missing_requirements && missing_requirements.length > 0 && (
                <div className="missing-requirements">
                    <h3 style={{ marginBottom: '1rem', color: 'var(--danger-red)' }}>
                        ⚠️ Missing Requirements
                    </h3>
                    {missing_requirements.map((req, index) => (
                        <div 
                            key={index} 
                            className="requirement-item stagger-enter"
                            style={{ animationDelay: `${(index + extracted_documents.length) * 0.1}s` }}
                        >
                            {req}
                        </div>
                    ))}
                </div>
            )}

            {/* Reasoning Result */}
            {reasoning_result && (
                <div style={{ marginTop: '2rem' }}>
                    {reasoning_result.recommendation && (
                        <div className="requirement-item stagger-enter" style={{ borderLeftColor: 'var(--secondary-teal)', animationDelay: '0.4s' }}>
                            <strong>💡 Recommendation</strong>
                            <p style={{ marginTop: '0.5rem' }}>{reasoning_result.recommendation}</p>
                        </div>
                    )}

                    {reasoning_result.explanation && (
                        <div className="requirement-item stagger-enter" style={{ borderLeftColor: 'var(--primary-blue)', animationDelay: '0.5s' }}>
                            <strong>📝 Explanation</strong>
                            <p style={{ marginTop: '0.5rem' }}>{reasoning_result.explanation}</p>
                        </div>
                    )}

                    {reasoning_result.simple_explanation && (
                        <div className="requirement-item stagger-enter" style={{ borderLeftColor: 'var(--primary-blue)', animationDelay: '0.6s' }}>
                            <strong>📝 Denial Explanation</strong>
                            <p style={{ marginTop: '0.5rem' }}>{reasoning_result.simple_explanation}</p>
                        </div>
                    )}

                    {reasoning_result.denial_code_meaning && (
                        <div className="requirement-item stagger-enter" style={{ borderLeftColor: 'var(--warning-yellow)', animationDelay: '0.7s' }}>
                            <strong>🔍 Denial Code Meaning</strong>
                            <p style={{ marginTop: '0.5rem' }}>{reasoning_result.denial_code_meaning}</p>
                        </div>
                    )}

                    {reasoning_result.next_steps && (
                        <div className="requirement-item stagger-enter" style={{ borderLeftColor: 'var(--success-green)', animationDelay: '0.8s' }}>
                            <strong>✅ Next Steps</strong>
                            <p style={{ marginTop: '0.5rem' }}>{reasoning_result.next_steps}</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default AnalysisResult;
