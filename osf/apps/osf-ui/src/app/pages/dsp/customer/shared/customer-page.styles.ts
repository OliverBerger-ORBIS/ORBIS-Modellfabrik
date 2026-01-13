/**
 * Shared styles for DSP customer pages
 * Optimized for 1920x1080 landscape video presentations
 */
export const CUSTOMER_PAGE_STYLES = `
  .customer-dsp-page {
    padding: 1rem;
    min-height: 100vh;
    background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
  }
  
  .customer-header {
    text-align: center;
    margin-bottom: 1rem;
  }
  
  .customer-header h1 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #164194;
    margin-bottom: 0.35rem;
  }
  
  .customer-header .subtitle {
    font-size: 0.875rem;
    color: #6b7280;
    margin: 0 0 0.75rem 0;
  }
  
  .view-mode-selector {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 0.75rem;
  }
  
  .view-mode-btn {
    padding: 0.4rem 1.25rem;
    border: 2px solid #164194;
    background: white;
    color: #164194;
    border-radius: 0.25rem;
    cursor: pointer;
    font-weight: 500;
    font-size: 0.875rem;
    transition: all 0.2s;
  }
  
  .view-mode-btn:hover {
    background: #f0f4ff;
  }
  
  .view-mode-btn.active {
    background: #164194;
    color: white;
  }
`;
