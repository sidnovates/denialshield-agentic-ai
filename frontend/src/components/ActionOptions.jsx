import React from 'react';

const ActionOptions = ({ options, onSelect }) => {
    return (
        <div className="premium-action-grid">
            {options.map((option, index) => (
                <div
                    key={index}
                    className={`premium-action-card theme-${option.theme || 'default'}`}
                    onClick={() => onSelect(option)}
                    style={{ animationDelay: `${index * 0.1}s` }}
                >
                    {option.icon && (
                        <div className="action-card-icon">{option.icon}</div>
                    )}

                    <div className="action-card-content">
                        <div className="action-card-label">{option.label}</div>
                        {option.subLabel && (
                            <div className="action-card-sublabel">{option.subLabel}</div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default ActionOptions;
