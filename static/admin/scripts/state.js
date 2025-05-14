// state.js
// Centralized state management

// Application state
const state = {
    currentPageId: null,
    pages: [],
    tags: []
};

// Getters
export const getCurrentPageId = () => state.currentPageId;
export const getPages = () => state.pages;
export const getTags = () => state.tags;

// Setters
export const setCurrentPageId = (id) => {
    state.currentPageId = id;
};

export const setPages = (newPages) => {
    state.pages = newPages;
};

export const setTags = (newTags) => {
    state.tags = newTags;
};

export const addTag = (tag) => {
    if (tag && !state.tags.includes(tag)) {
        state.tags.push(tag);
        return true;
    }
    return false;
};

export const removeTag = (tagToRemove) => {
    state.tags = state.tags.filter(tag => tag !== tagToRemove);
};