import React, { useState, useEffect, useRef } from 'react';
import ChatInterface from './components/ChatInterface';
import FileUpload from './components/FileUpload';
import ActionOptions from './components/ActionOptions';
import AnalysisResult from './components/AnalysisResult';
import SimulationResult from './components/SimulationResult';
import AppealDetailsForm from './components/AppealDetailsForm';
import { uploadFiles, analyzeDocuments, generateAppealLetter, getInsurancePlans, clearUploads, getDocuments, savePolicy, getPolicy, runSimulation } from './services/api';
import logo from './assets/logo.png';
import './App.css';

function App() {
    const [messages, setMessages] = useState([]);
    const [isTyping, setIsTyping] = useState(false);

    // State Machine
    const [workflow, setWorkflow] = useState(null); // 'pre_claim', 'denial_explanation', 'appeal'
    const [uploadedDocs, setUploadedDocs] = useState([]);
    const [selectedPolicy, setSelectedPolicy] = useState(null);

    const hasInitialized = useRef(false);
    // Keep refs to latest state to avoid closure issues
    const uploadedDocsRef = useRef([]);
    const workflowRef = useRef(null);
    const selectedPolicyRef = useRef(null);
    const currentCategoryRef = useRef("PreClaim"); // "PreClaim", "Denial"


    // Initial Greeting
    useEffect(() => {
        if (!hasInitialized.current) {
            hasInitialized.current = true;
            initChat();
        }
    }, []);

    const initChat = async () => {
        await typeMessage('👋 Hi! I\'m Hackios, your health insurance assistant.');
        await showMainOptions();
    };

    // Helper to generate main menu options
    const showMainOptions = async () => {
        await typeMessage('What can I help you with today?', false, (
            <ActionOptions
                options={[
                    { label: '🔍 Pre-Claim Analysis', value: 'pre_claim' },
                    { label: '🔮 Claim Simulator', value: 'simulator' },
                    { label: '📋 Denial Explanation', value: 'denial_explanation' },
                    { label: '✍️ Appeal Letter', value: 'appeal' }
                ]}
                onSelect={handleWorkflowSelect}
            />
        ));
    };

    // Helper to simulate typing delay
    const typeMessage = (content, isUser = false, component = null) => {
        return new Promise((resolve) => {
            if (!isUser) setIsTyping(true);

            setTimeout(() => {
                const msg = {
                    type: isUser ? 'user' : 'bot',
                    content: component || content
                };
                setMessages(prev => [...prev, msg]);
                if (!isUser) setIsTyping(false);
                resolve();
            }, isUser ? 0 : 1200);
        });
    };

    const handleWorkflowSelect = async (option) => {
        await typeMessage(option.label, true); // User reply
        setWorkflow(option.value);
        workflowRef.current = option.value; // Update ref to avoid closure issues

        // --- INTELLIGENT WORKFLOW LOGIC ---

        // CASE 1: Pre-Claim -> ALWAYS FRESH START
        if (option.value === 'pre_claim') {
            // Clear 'PreClaim' for fresh start
            await clearUploads('PreClaim');

            // Set Category
            currentCategoryRef.current = 'PreClaim';

            // Reset State
            setUploadedDocs([]);
            uploadedDocsRef.current = [];
            setSelectedPolicy(null);
            selectedPolicyRef.current = null;

            await typeMessage('To start the pre-claim analysis, please upload your **medical bill** and **doctor\'s notes**.');
            await typeMessage(null, false, (
                <FileUpload
                    placeholder="Upload PDF or Images"
                    onFilesSelected={handleDocUpload}
                />
            ));
        }

        // CASE 2: Simulator -> FRESH START (like pre_claim)
        else if (option.value === 'simulator') {
            await clearUploads('PreClaim');
            currentCategoryRef.current = 'PreClaim';
            setUploadedDocs([]);
            uploadedDocsRef.current = [];
            setSelectedPolicy(null);
            selectedPolicyRef.current = null;

            await typeMessage('🔮 Let\'s simulate your claim outcome. I can tell you your approval odds and how to improve them.');
            await typeMessage('Start by uploading your **medical bill** and **doctor\'s notes**.');

            await typeMessage(null, false, (
                <FileUpload
                    placeholder="Load Documents for Simulation"
                    onFilesSelected={handleDocUpload}
                />
            ));
        }

        // CASE 2: Denial Explanation or Appeal -> INTELLIGENT CONTEXT
        else {
            let hasPreClaim = false;
            let hasPolicy = false;
            let hasDenial = false;
            let savedPolicy = null;

            // 1. Check Policy
            const policyResponse = await getPolicy();
            if (policyResponse.success && policyResponse.policy_id) {
                savedPolicy = policyResponse.policy_id;
                hasPolicy = true;
                console.log('Found saved policy:', savedPolicy);
            }

            // 2. Check Pre-Claim Docs
            let preClaimDocs = [];
            const preClaimResponse = await getDocuments('PreClaim');
            if (preClaimResponse.success && preClaimResponse.files.length > 0) {
                preClaimDocs = preClaimResponse.files;
                hasPreClaim = true;
                console.log('Found Pre-Claim docs:', preClaimDocs);
            }

            // 3. Check Denial Docs (New logic for Appeal/Denial context)
            let denialDocs = [];
            const denialResponse = await getDocuments('Denial');
            if (denialResponse.success && denialResponse.files.length > 0) {
                denialDocs = denialResponse.files;
                hasDenial = true;
                console.log('Found Denial docs:', denialDocs);
            }

            // --- WORKFLOW ROUTING ---

            // IF APPEAL: We need EVERYTHING (PreClaim + Policy + Denial)
            if (option.value === 'appeal') {
                if (hasPreClaim && hasPolicy && hasDenial) {
                    // restore full context
                    const allDocs = [...preClaimDocs, ...denialDocs];
                    setUploadedDocs(allDocs);
                    uploadedDocsRef.current = allDocs;
                    setSelectedPolicy(savedPolicy);
                    selectedPolicyRef.current = savedPolicy;

                    await typeMessage(`I have all the necessary documents (Bill, Notes, Denial Letter) and your policy.`);
                    await offerAppealGeneration(allDocs.map(d => d.id), savedPolicy);
                    return;
                }

                // Missing something? Fall through to intelligent prompts...
            }

            // Logic: Do we have enough context to skip to Denial Letter?
            // "PreClaim" files exist AND Policy exists.
            if (hasPreClaim && hasPolicy) {
                // Restore Context (PreClaim)
                setUploadedDocs(preClaimDocs);
                uploadedDocsRef.current = preClaimDocs;

                setSelectedPolicy(savedPolicy);
                selectedPolicyRef.current = savedPolicy;

                // Did we already have the Denial Letter too?
                if (hasDenial) {
                    // If we are just doing Denial Explanation, we are ready to run
                    const allDocs = [...preClaimDocs, ...denialDocs];
                    setUploadedDocs(allDocs);
                    uploadedDocsRef.current = allDocs;
                    await typeMessage(`I found your previous bill, notes, policy, AND denial letter.`);
                    runAnalysis(savedPolicy);
                } else {
                    // We need the Denial Letter
                    currentCategoryRef.current = 'Denial';
                    await typeMessage(`I found your previous bill, notes, and policy preference (${savedPolicy}).`);
                    await typeMessage('Please upload just your **denial letter** now to proceed.');

                    await typeMessage(null, false, (
                        <FileUpload
                            placeholder="Upload document(s)"
                            onFilesSelected={handleDocUpload}
                        />
                    ));
                }
            }
            else {
                // Not enough context -> Start Fresh (or Semi-Fresh)

                // Set category to PreClaim first (for Bill/Notes)
                currentCategoryRef.current = 'PreClaim';

                // Reset State
                setUploadedDocs([]);
                uploadedDocsRef.current = [];
                setSelectedPolicy(null);
                selectedPolicyRef.current = null;

                // Prompt
                let promptText = '';
                if (option.value === 'denial_explanation') {
                    // Step 1: Bill & Notes
                    promptText = 'To explain your denial, I first need context. Please upload your **medical bill** and **doctor\'s notes**.';
                } else {
                    // Appeal - Implicitly needs same start
                    promptText = 'To generate an appeal letter, I first need the case context. Please upload your **medical bill** and **doctor\'s notes**.';
                }
                await typeMessage(promptText);

                // Show upload button
                await typeMessage(null, false, (
                    <FileUpload
                        placeholder="Upload document(s)"
                        onFilesSelected={handleDocUpload}
                    />
                ));
            }
        }
    };

    const handleDocUpload = async (files) => {
        // Optimistic UI update
        await typeMessage(`📤 Uploading and processing ${files.length} document(s)... This may take a moment.`, true);

        setIsTyping(true);
        try {
            // Use current category from ref
            const category = currentCategoryRef.current;
            console.log(`Uploading to category: ${category}`);
            const response = await uploadFiles(files, category);
            console.log('Upload response:', response); // DEBUG
            setIsTyping(false);

            if (response.success && response.files) {
                console.log('Files to add to state:', response.files); // DEBUG
                await typeMessage('✅ Received and processed files successfully.');

                // Update state with uploaded documents (APPEND MODE)
                const newDocs = response.files;

                setUploadedDocs(prev => {
                    const updated = [...prev, ...newDocs];
                    console.log('Updated uploadedDocs state:', updated); // DEBUG
                    return updated;
                });

                // CRITICAL FIX: Update ref IMMEDIATELY so it's ready for the next line
                // The setUploadedDocs callback runs asynchronously/later, which is too late for runAnalysis below
                const currentDocs = uploadedDocsRef.current;
                const updatedDocsSync = [...currentDocs, ...newDocs];
                uploadedDocsRef.current = updatedDocsSync;
                console.log('Updated uploadedDocsRef synchronously:', updatedDocsSync); // DEBUG

                // Next Step Logic
                // If we already have a policy, we might be in the second phase of Denial Explanation (uploading Denial Letter)
                // OR we are in a transition flow.
                if (selectedPolicyRef.current) {
                    // INTELLIGENT ROUTING FOR APPEAL
                    if (workflowRef.current === 'appeal') {
                        if (currentCategoryRef.current === 'Denial') {
                            // We just uploaded the final piece
                            const allDocs = uploadedDocsRef.current;
                            await typeMessage('✅ Denial letter received. I have everything needed now.');
                            await offerAppealGeneration(allDocs.map(d => d.id), selectedPolicyRef.current);
                        } else {
                            // We uploaded PreClaim but had a policy already? Ask for Denial.
                            currentCategoryRef.current = 'Denial';
                            await typeMessage('Got the context. Now please upload the **Denial Letter**.');
                            await typeMessage(null, false, (
                                <FileUpload
                                    placeholder="Upload Denial Letter"
                                    onFilesSelected={handleDocUpload}
                                />
                            ));
                        }
                    }
                    // INTELLIGENT ROUTING FOR DENIAL EXPLANATION
                    else if (workflowRef.current === 'denial_explanation' && currentCategoryRef.current === 'PreClaim') {
                        // We just uploaded PreClaim, now we need Denial (Policy is already known)
                        currentCategoryRef.current = 'Denial';
                        await typeMessage('Got the context. Now please upload the **Denial Letter**.');
                        await typeMessage(null, false, (
                            <FileUpload
                                placeholder="Upload Denial Letter"
                                onFilesSelected={handleDocUpload}
                            />
                        ));
                    }
                    else {
                        // Normal flow (Pre-Claim Analysis OR Final step of Denial Explanation)
                        runAnalysis(selectedPolicyRef.current);
                    }
                } else {
                    // Normal flow: We need a policy
                    askForPolicy();
                }

            } else {
                console.error('Upload failed or no files in response:', response);
                await typeMessage('❌ Upload failed. Please try again.');
            }
        } catch (error) {
            console.error('Upload error:', error);
            setIsTyping(false);
            await typeMessage('❌ Error uploading files.');
        }
    };

    const askForPolicy = async () => {
        await typeMessage('Which insurance policy should we check against?');
        await typeMessage(null, false, (
            <ActionOptions
                options={[
                    { label: 'Aetna PPO', value: 'aetna_ppo' },
                    { label: 'BlueCross PPO', value: 'bluecross_ppo' },
                    { label: 'UnitedHealthcare', value: 'unitedhealthcare' },
                    { label: '📄 Upload Policy Doc', value: 'UPLOAD_CUSTOM' }
                ]}
                onSelect={handlePolicySelect}
            />
        ));
    };

    const handlePolicySelect = async (option) => {
        await typeMessage(option.label, true);

        if (option.value === 'UPLOAD_CUSTOM') {
            await typeMessage('Please upload your full insurance policy document (PDF).');
            await typeMessage(null, false, (
                <FileUpload
                    placeholder="Upload Policy PDF"
                    onFilesSelected={handlePolicyUpload}
                />
            ));
        } else {
            setSelectedPolicy(option.value);
            selectedPolicyRef.current = option.value;

            // Save policy preference to backend
            savePolicy(option.value);

            // NEW LOGIC: Intercept Denial Explanation Flow OR Appeal Flow
            if (workflowRef.current === 'denial_explanation' || workflowRef.current === 'appeal') {
                // Step 3: Now ask for Denial Letter
                // Set appropriate category
                currentCategoryRef.current = 'Denial';

                await typeMessage('Great. Now please upload your **Denial Letter** so I can analyze it.');
                await typeMessage(null, false, (
                    <FileUpload
                        placeholder="Upload Denial Letter"
                        onFilesSelected={handleDocUpload}
                    />
                ));
            } else {
                // Pre-claim (standard flow)
                runAnalysis(option.value);
            }
        }
    };

    const handlePolicyUpload = async (files) => {
        setIsTyping(true);
        try {
            // Policy mainly relevant for PreClaim context, so save there
            const response = await uploadFiles(files, 'PreClaim');
            setIsTyping(false);

            if (response.success) {
                // Assuming backend can handle custom policy analysis if passed as a doc ID
                // For now, in this mock logic, we'll treat it as a generic "Custom Policy"
                await typeMessage('✅ Policy document uploaded.');
                setSelectedPolicy('custom_uploaded');
                selectedPolicyRef.current = 'custom_uploaded';

                // Same interception logic for Custom Policy upload
                if (workflowRef.current === 'denial_explanation' || workflowRef.current === 'appeal') {
                    // Set appropriate category
                    currentCategoryRef.current = 'Denial';

                    await typeMessage('Great. Now please upload your **Denial Letter** so I can analyze it.');
                    await typeMessage(null, false, (
                        <FileUpload
                            placeholder="Upload Denial Letter"
                            onFilesSelected={handleDocUpload}
                        />
                    ));
                } else {
                    runAnalysis('custom_uploaded');
                }
            }
        } catch (e) {
            setIsTyping(false);
            await typeMessage('❌ Error uploading policy.');
        }
    };

    const runAnalysis = async (policyId) => {
        // Use ref to get latest uploaded docs (avoids closure issues)
        const currentDocs = uploadedDocsRef.current;
        console.log('runAnalysis - checking docs:', currentDocs); // DEBUG

        if (currentDocs.length === 0) {
            await typeMessage("⚠️ I don't see any uploaded documents to analyze. Please upload them first.");
            // Loop back to main menu even on error, so user isn't stuck
            setTimeout(() => showMainOptions(), 1000);
            return;
        }

        await typeMessage('🔍 Analyzing your documents against the policy...');

        setIsTyping(true);
        const docIds = currentDocs.map(d => d.id);

        // Map interactive workflow names to backend expectations
        // Use ref to get current workflow (avoid closure issues)
        const currentWorkflow = workflowRef.current || 'pre_claim'; // Default to pre_claim
        console.log('Current workflow from ref:', currentWorkflow); // DEBUG

        let backendWorkflow = currentWorkflow;
        if (currentWorkflow === 'appeal') {
            // Appeal usually implies detailed analysis first
            backendWorkflow = 'denial_explanation';
        }

        // Handle Simulation Workflow
        if (currentWorkflow === 'simulator') {
            await typeMessage('🔮 Running counterfactual simulation (this uses advanced reasoning)...');
            setIsTyping(true);
            try {
                console.log('Calling runSimulation with:', { docIds, policyId });
                const result = await runSimulation(docIds, policyId);
                setIsTyping(false);

                if (result.status === 'success' || result.data) {
                    await typeMessage('Simulation Complete! Here are your scenarios:');
                    await typeMessage(null, false, <SimulationResult result={result} />);
                } else {
                    await typeMessage('⚠️ Simulation returned no data. Please ensure documents have clinical info.');
                }
            } catch (e) {
                setIsTyping(false);
                console.error(e);
                await typeMessage('❌ Error running simulation.');
            } finally {
                setTimeout(() => showMainOptions(), 3000);
            }
            return;
        }

        try {
            console.log('Calling analyzeDocuments with:', { docIds, policyId, analysis_type: backendWorkflow }); // DEBUG
            const result = await analyzeDocuments(docIds, policyId, backendWorkflow);
            setIsTyping(false);

            if (result.success) {
                await typeMessage('Analysis Complete! Here is what I found:');
                await typeMessage(null, false, <AnalysisResult result={result} />);

                if (workflow === 'appeal') {
                    // Logic for appeal flow usually ends with generation, but let's offer it
                    await offerAppealGeneration(docIds, policyId);
                } else if (result.missing_requirements && result.missing_requirements.length > 0) {
                    await typeMessage('⚠️ Missing information detected. You should ask your doctor for these specifically.');
                }
            }
        } catch (error) {
            setIsTyping(false);
            console.error(error);
            await typeMessage('❌ Sorry, something went wrong during analysis.');
        } finally {
            // --- LOOP BACK TO MAIN MENU ---
            // Wait a moment so the user can read the result, then show options again
            setTimeout(() => {
                showMainOptions();
            }, 2000);
        }
    };

    const offerAppealGeneration = async (docIds, policyId) => {
        await typeMessage('I have prepared the medical arguments.');
        // Import dynamically if needed, or better, add import at top. 
        // For inline edit, assuming import is added.
        await typeMessage(null, false, (
            <div className="appeal-form-container">
                {/* We will need to import this at the top of the file */}
                <AppealDetailsForm onGenerate={(details) => generatePDF(docIds, policyId, details)} />
            </div>
        ));
    };

    const generatePDF = async (docIds, policyId, userDetails) => {
        await typeMessage('Generating Appeal Letter PDF...', true);
        setIsTyping(true);
        try {
            const blob = await generateAppealLetter(docIds, policyId, userDetails);
            setIsTyping(false);

            // Create download link
            const url = window.URL.createObjectURL(blob);
            await typeMessage(null, false, (
                <div className="download-success-card">
                    {/* Confetti Particles */}
                    <div className="confetti c-1"></div>
                    <div className="confetti c-2"></div>
                    <div className="confetti c-3"></div>
                    <div className="confetti c-4"></div>
                    <div className="confetti c-5"></div>

                    <div className="success-icon-wrapper">
                        ✓
                    </div>

                    <h3 className="success-title">Appeal Letter Ready!</h3>
                    <p className="success-subtitle">
                        Your professionally formatted document has been generated.
                    </p>

                    <a href={url} download="Appeal_Letter.pdf" className="btn-download-premium">
                        <span>📥</span> Download Official PDF
                    </a>
                </div>
            ));
        } catch (e) {
            setIsTyping(false);
            console.error(e);
            await typeMessage('❌ Failed to generate PDF.');
        }
    };

    return (
        <div className="app-container">
            <header className="app-header">
                <div className="brand-container">
                    <img src={logo} alt="DenialShield Logo" className="app-logo" />
                    <h1>DenialShield</h1>
                </div>
                <span className="badge">AI Defense Agent</span>
            </header>
            <main className="main-chat">
                <ChatInterface messages={messages} isTyping={isTyping} />
            </main>
        </div>
    );
}

export default App;
