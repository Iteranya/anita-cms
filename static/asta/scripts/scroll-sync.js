// scroll-sync.js
// Synchronized scrolling between editor and preview

export class ScrollSynchronizer {
    constructor(sourceElement, targetElement) {
        this.source = sourceElement;
        this.target = targetElement;
        this.isSyncingSourceScroll = false;
        this.isSyncingTargetScroll = false;
        this.syncTimeout = null;
        
        // Set up event listeners
        this.source.addEventListener('scroll', () => this.handleSourceScroll());
        this.target.addEventListener('scroll', () => this.handleTargetScroll());
    }
    
    handleSourceScroll() {
        this.syncScroll(
            this.source, 
            this.target, 
            this.isSyncingSourceScroll, 
            (val) => this.isSyncingTargetScroll = val
        );
    }
    
    handleTargetScroll() {
        this.syncScroll(
            this.target, 
            this.source, 
            this.isSyncingTargetScroll, 
            (val) => this.isSyncingSourceScroll = val
        );
    }
    
    syncScroll(source, target, isSyncingSourceFlag, setIsSyncingTargetFlag) {
        clearTimeout(this.syncTimeout);
        
        if (isSyncingSourceFlag) {
            // If this scroll event was triggered by the other pane, reset the flag and do nothing
            return false;
        }
        
        // Debounce the scroll syncing slightly
        this.syncTimeout = setTimeout(() => {
            const sourceScrollHeight = source.scrollHeight - source.clientHeight;
            const targetScrollHeight = target.scrollHeight - target.clientHeight;
            
            // Avoid division by zero and unnecessary calculations
            if (sourceScrollHeight <= 0 || targetScrollHeight <= 0) return;
            
            const scrollPercentage = source.scrollTop / sourceScrollHeight;
            const targetScrollTop = scrollPercentage * targetScrollHeight;
            
            // Set the flag for the target before programmatically scrolling
            setIsSyncingTargetFlag(true);
            target.scrollTop = targetScrollTop;
            
            // Add a small delay before resetting the flag to avoid immediate reciprocal sync
            setTimeout(() => setIsSyncingTargetFlag(false), 50);
        }, 20); // 20ms debounce time
    }
}