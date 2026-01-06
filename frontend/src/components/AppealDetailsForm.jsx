import React, { useState } from 'react';

const AppealDetailsForm = ({ onGenerate }) => {
    const [formData, setFormData] = useState({
        senderName: '',
        senderAddress: '',
        senderCityStateZip: '',
        senderEmail: '',
        senderPhone: '',
        recipientName: '',
        recipientTitle: '',
        recipientOrg: '',
        recipientAddress: ''
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onGenerate(formData);
    };

    return (
        <div className="appeal-form-container">
            <div className="form-header">
                <h3 className="form-title">Finalize Your Appeal</h3>
                <p className="form-subtitle">
                    Provide the official details to generate your professional legal document.
                </p>
            </div>

            <form onSubmit={handleSubmit}>
                {/* Sender Information Section */}
                <div className="form-section" style={{ animationDelay: '0.1s' }}>
                    <div className="form-section-title">Your Information</div>

                    <div className="form-grid">
                        <div className="input-group">
                            <input
                                type="text"
                                name="senderName"
                                className="input-field"
                                placeholder=" "
                                value={formData.senderName}
                                onChange={handleChange}
                                required
                            />
                            <label className="input-label">Full Name</label>
                        </div>
                        <div className="input-group">
                            <input
                                type="text"
                                name="senderPhone"
                                className="input-field"
                                placeholder=" "
                                value={formData.senderPhone}
                                onChange={handleChange}
                                required
                            />
                            <label className="input-label">Phone Number</label>
                        </div>
                    </div>

                    <div className="input-group">
                        <input
                            type="email"
                            name="senderEmail"
                            className="input-field"
                            placeholder=" "
                            value={formData.senderEmail}
                            onChange={handleChange}
                            required
                        />
                        <label className="input-label">Email Address</label>
                    </div>

                    <div className="form-grid">
                        <div className="input-group">
                            <input
                                type="text"
                                name="senderAddress"
                                className="input-field"
                                placeholder=" "
                                value={formData.senderAddress}
                                onChange={handleChange}
                                required
                            />
                            <label className="input-label">Street Address</label>
                        </div>
                        <div className="input-group">
                            <input
                                type="text"
                                name="senderCityStateZip"
                                className="input-field"
                                placeholder=" "
                                value={formData.senderCityStateZip}
                                onChange={handleChange}
                                required
                            />
                            <label className="input-label">City, State, ZIP</label>
                        </div>
                    </div>
                </div>

                {/* Recipient Information Section */}
                <div className="form-section" style={{ animationDelay: '0.2s' }}>
                    <div className="form-section-title">Recipient Details (Optional)</div>

                    <div className="form-grid">
                        <div className="input-group">
                            <input
                                type="text"
                                name="recipientName"
                                className="input-field"
                                placeholder=" "
                                value={formData.recipientName}
                                onChange={handleChange}
                            />
                            <label className="input-label">Recipient Name</label>
                        </div>
                        <div className="input-group">
                            <input
                                type="text"
                                name="recipientTitle"
                                className="input-field"
                                placeholder=" "
                                value={formData.recipientTitle}
                                onChange={handleChange}
                            />
                            <label className="input-label">Title / Department</label>
                        </div>
                    </div>

                    <div className="input-group">
                        <input
                            type="text"
                            name="recipientOrg"
                            className="input-field"
                            placeholder=" "
                            value={formData.recipientOrg}
                            onChange={handleChange}
                            required
                        />
                        <label className="input-label">Organization Name</label>
                    </div>

                    <div className="input-group">
                        <input
                            type="text"
                            name="recipientAddress"
                            className="input-field"
                            placeholder=" "
                            value={formData.recipientAddress}
                            onChange={handleChange}
                            required
                        />
                        <label className="input-label">Organization Address</label>
                    </div>
                </div>

                <div className="form-section" style={{ animationDelay: '0.3s' }}>
                    <button type="submit" className="btn-generate">
                        <span className="sparkle-icon">✨</span> Generate Official Appeal
                    </button>
                </div>
            </form>
        </div>
    );
};

export default AppealDetailsForm;
