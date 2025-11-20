const API_BASE_URL = '/admin/api/page';

/**
 * Fetch all projects
 * @returns {Promise<Array>} List of projects
 */
export async function listProjects() {
  const response = await fetch(`${API_BASE_URL}/list`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch projects: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Get a specific project by slug
 * @param {string} slug - Project unique identifier
 * @returns {Promise<Object>} Project data
 */
export async function getProject(slug) {
  const response = await fetch(`${API_BASE_URL}/${slug}`);
  
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Project "${slug}" not found`);
    }
    throw new Error(`Failed to fetch project: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Update an existing project
 * @param {string} slug - Project slug to update
 * @param {Object} projectData - Updated project data
 * @returns {Promise<Object>} Updated project data
 */
export async function updateProject(slug, projectData) {
  const response = await fetch(`${API_BASE_URL}/${slug}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(projectData),
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Project "${slug}" not found`);
    }
    throw new Error(`Failed to update project: ${response.statusText}`);
  }

  const project = await response.json();

  return { project};
}

/**
 * Delete a project
 * @param {string} slug - Project slug to delete
 * @returns {Promise<Object>} Deletion confirmation
 */
export async function deleteProject(slug) {
  const response = await fetch(`${API_BASE_URL}/${slug}`, {
    method: 'DELETE',
  });
  
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Project "${slug}" not found`);
    }
    throw new Error(`Failed to delete project: ${response.statusText}`);
  }
  
  return response.json();
}