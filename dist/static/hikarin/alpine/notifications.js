export default {
    items: [],
    
    success(title, message = '') {
        this.add('success', title, message);
    },

    error(title, errorObj = null) {
        let message = "Something went wrong.";
        
        if (typeof errorObj === 'string') {
            message = errorObj;
        } else if (errorObj && errorObj.detail) {
            message = errorObj.detail;
        } else if (errorObj && errorObj.message) {
            message = errorObj.message;
        }
        
        this.add('error', title, message);
    },

    info(title, message = '') {
        this.add('info', title, message);
    },

    add(type, title, message) {
        const id = Date.now();
        this.items.push({ id, type, title, message });
        
        setTimeout(() => {
            this.remove(id);
        }, 4000);
    },

    remove(id) {
        this.items = this.items.filter(item => item.id !== id);
    }
}