/**
 * API Service for communicating with the backend
 */
import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Upload files to the backend
 */
export const uploadFiles = async (files, category) => {
    const formData = new FormData();
    files.forEach((file) => {
        formData.append('files', file);
    });

    formData.append("category", category);

    const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    console.log(response.data)
    return response.data;
};

/**
 * Clear uploaded files from server
 */
export const clearUploads = async () => {
    try {
        const response = await api.post('/upload/clear');
        return response.data;
    } catch (error) {
        console.error('Error clearing uploads:', error);
        return { success: false };
    }
};

/**
 * Get list of existing documents from server
 * @param {string} category - Optional category to filter
 */
export const getDocuments = async (category = null) => {
    try {
        const url = category ? `/upload/documents?category=${category}` : '/upload/documents';
        const response = await api.get(url);
        return response.data;
    } catch (error) {
        console.error('Error fetching documents:', error);
        return { success: false, files: [] };
    }
};

/**
 * Save user policy preference
 */
export const savePolicy = async (policyId) => {
    try {
        const response = await api.post('/session/policy', { policy_id: policyId });
        return response.data;
    } catch (error) {
        console.error('Error saving policy:', error);
        return { success: false };
    }
};

/**
 * Get saved user policy
 */
export const getPolicy = async () => {
    try {
        const response = await api.get('/session/policy');
        return response.data;
    } catch (error) {
        console.error('Error getting policy:', error);
        return { success: false, policy_id: null };
    }
};

/**
 * Analyze uploaded documents
 */
export const analyzeDocuments = async (documentIds, insurancePlan, analysisType) => {
    const response = await api.post('/analyze', {
        document_ids: documentIds,
        insurance_plan: insurancePlan,
        analysis_type: analysisType,
    });

    return response.data;
};

/**
 * Generate appeal letter
 */
export const generateAppealLetter = async (documentIds, insurancePlan, userDetails) => {
    const response = await axios.post(
        `${API_BASE_URL}/appeal-letter`,
        {
            document_ids: documentIds,
            insurance_plan: insurancePlan,
            user_details: userDetails
        },
        {
            responseType: 'blob', // Important for PDF download
        }
    );

    return response.data;
};

/**
 * Get available insurance plans
 */
export const getInsurancePlans = async () => {
    const response = await api.get('/insurance-plans');
    return response.data;
};

export default api;
