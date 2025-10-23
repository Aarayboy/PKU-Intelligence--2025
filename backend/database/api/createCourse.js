// function/createCourse.js - 新建课程

/**
 * 新建课程 - 根据数据库格式对齐
 * @param {string} name - 课程名称 (对应Course表的name字段)
 * @param {Array} tags - 标签数组 (对应Course表的tags字段)
 * @param {string} classTime - 上课时间 (对应Course表的classTime字段)
 * @param {string} baseUrl - API基础URL
 * @param {Object} options - 可选配置
 * @returns {Promise<Object>} 创建结果
 */
export async function createCourse(name, tags, classTime = '', baseUrl = 'https://example.com', options = {}) {
  try {
    const formData = new FormData();
    // 使用数据库字段名
    formData.append('name', name);           // 对应 Course.name
    formData.append('tags', JSON.stringify(tags)); // 对应 Course.tags
    formData.append('classTime', classTime); // 对应 Course.classTime

    const headers = {};
    if (options.token) {
      headers['Authorization'] = `Bearer ${options.token}`;
    }

    const response = await fetch(`${baseUrl}/courses/create`, {
      method: 'POST',
      body: formData,
      headers: headers,
      credentials: options.includeCredentials ? 'include' : 'same-origin'
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`创建课程失败: ${response.status} ${response.statusText} - ${errorText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('创建课程时发生错误:', error);
    throw error;
  }
}

/**
 * 获取所有课程列表
 * @param {string} baseUrl - API基础URL
 * @param {Object} options - 可选配置
 * @returns {Promise<Array>} 课程列表
 */
export async function getAllCourses(baseUrl = 'https://example.com', options = {}) {
  try {
    const headers = {
      'Accept': 'application/json'
    };

    if (options.token) {
      headers['Authorization'] = `Bearer ${options.token}`;
    }

    const response = await fetch(`${baseUrl}/courses`, {
      method: 'GET',
      headers: headers,
      credentials: options.includeCredentials ? 'include' : 'same-origin'
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`获取课程列表失败: ${response.status} ${response.statusText} - ${errorText}`);
    }

    const courses = await response.json();
    return courses;
  } catch (error) {
    console.error('获取课程列表时发生错误:', error);
    throw error;
  }
}