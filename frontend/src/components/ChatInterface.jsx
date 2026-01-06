import React, { useEffect, useRef } from 'react';

const ChatInterface = ({ messages, isTyping }) => {
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    return (
        <div className="chat-container glass-card">
            <div className="chat-messages">
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`message ${message.type === 'user' ? 'message-user' : 'message-bot'}`}
                        style={{
                            animation: 'springSlideIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
                            opacity: 0
                        }}
                    >
                        <div className="message-avatar">
                            {message.type === 'user' ? '👤' : '🤖'}
                        </div>
                        <div className="message-content">
                            {typeof message.content === 'string' ? (
                                <p>
                                    {message.content.split(/(\*\*.*?\*\*)/).map((part, i) =>
                                        part.startsWith('**') && part.endsWith('**') ?
                                            <strong key={i}>{part.slice(2, -2)}</strong> :
                                            <span key={i}>{part}</span>
                                    )}
                                </p>
                            ) : (
                                message.content
                            )}
                        </div>
                    </div>
                ))}

                {isTyping && (
                    <div className="message message-bot" style={{ animation: 'springSlideIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards' }}>
                        <div className="message-avatar">🤖</div>
                        <div className="message-content typing-indicator">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>
        </div>
    );
};

export default ChatInterface;
