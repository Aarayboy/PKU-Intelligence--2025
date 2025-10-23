// function/getUserData.js - 获取用户数据

/**
 * 获取用户数据 - 根据数据库格式对齐
 * @param {string} userId - 用户ID
 * @param {string} baseUrl - API基础URL
 * @param {Object} options - 可选配置
 * @returns {Promise<Object>} 用户数据
 */
export async function getUserData(userId, baseUrl = 'https://example.com', options = {}) {
  try {
    const headers = {
      'Accept': 'application/json'
    };

    if (options.token) {
      headers['Authorization'] = `Bearer ${options.token}`;
    }

    // 根据你的数据库，需要传递用户ID来获取特定用户数据
    const response = await fetch(`${baseUrl}/userdata/${userId}`, {
      method: 'GET',
      headers: headers,
      credentials: options.includeCredentials ? 'include' : 'same-origin'
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`获取用户数据失败: ${response.status} ${response.statusText} - ${errorText}`);
    }

    const userData = await response.json();
    
    // 返回的数据对应你的UserData表结构
    return userData;
  } catch (error) {
    console.error('获取用户数据时发生错误:', error);
    throw error;
  }
}

/**
 * 获取完整用户信息（包括课程详情和笔记）
 * @param {string} userId - 用户ID
 * @param {string} baseUrl - API基础URL
 * @param {Object} options - 可选配置
 * @returns {Promise<Object>} 完整的用户信息
 */
export async function getFullUserData(userId, baseUrl = 'https://example.com', options = {}) {
  try {
    const headers = {
      'Accept': 'application/json'
    };

    if (options.token) {
      headers['Authorization'] = `Bearer ${options.token}`;
    }

    // 获取包含课程详情和笔记的完整用户数据
    const response = await fetch(`${baseUrl}/userdata/${userId}/full`, {
      method: 'GET',
      headers: headers,
      credentials: options.includeCredentials ? 'include' : 'same-origin'
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`获取完整用户数据失败: ${response.status} ${response.statusText} - ${errorText}`);
    }

    const fullUserData = await response.json();
    return fullUserData;
  } catch (error) {
    console.error('获取完整用户数据时发生错误:', error);
    throw error;
  }
}