/**
 * Shared styles for DSP customer pages
 */
export const CUSTOMER_PAGE_STYLES = `
  .customer-dsp-page {
    padding: 2rem;
    min-height: 100vh;
    background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
  }
  
  .customer-header {
    text-align: center;
    margin-bottom: 2rem;
  }
  
  .customer-header h1 {
    font-size: 2rem;
    font-weight: 600;
    color: #164194;
    margin-bottom: 0.5rem;
  }
  
  .customer-header .subtitle {
    font-size: 1rem;
    color: #6b7280;
    margin: 0 0 1rem 0;
  }
  
  .view-mode-selector {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 1rem;
  }
  
  .view-mode-btn {
    padding: 0.5rem 1.5rem;
    border: 2px solid #164194;
    background: white;
    color: #164194;
    border-radius: 0.25rem;
    cursor: pointer;
    font-weight: 500;
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
