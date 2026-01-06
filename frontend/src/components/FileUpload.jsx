import React, { useState, useRef } from 'react';

const FileUpload = ({ onFilesSelected, autoTrigger = false, placeholder = "Upload documents...", accept = ".pdf,.jpg,.jpeg,.png" }) => {
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef(null);

    const handleFileChange = (event) => {
        const files = Array.from(event.target.files);
        if (files.length > 0) {
            handleFiles(files);
        }
    };

    const handleFiles = (files) => {
        if (onFilesSelected) {
            onFilesSelected(files);
        }
    };

    const handleDragEnter = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) {
            handleFiles(files);
        }
    };

    return (
        <div className="chat-upload-container">
            <div
                className={`chat-upload-zone ${isDragging ? 'dragover' : ''}`}
                onDragEnter={handleDragEnter}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current.click()}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept={accept}
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                />
                <div className="chat-upload-content">
                    <div className="upload-icon-wrapper">
                        <span className="upload-icon">📎</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                        <span className="upload-text">{isDragging ? "Drop files now" : placeholder}</span>
                        <span className="upload-subtext">Drag & drop or click to browse</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FileUpload;
