// function/uploadNote.js - 上传笔记

/**
 * 上传笔记 - 根据数据库格式对齐
 * @param {string} name - 笔记名称 (对应MyNote表的name字段)
 * @param {string} lessonName - 课程名称 (对应MyNote表的lessonName字段)
 * @param {File} file - 笔记文件
 * @param {string} baseUrl - API基础URL
 * @param {Object} options - 可选配置
 * @returns {Promise<Object>} 上传结果
 */
export async function uploadNote(name, lessonName, file, baseUrl = 'https://example.com', options = {}) {
  try {
    const formData = new FormData();
    // 使用数据库字段名
    formData.append('name', name);           // 对应 MyNote.name
    formData.append('lessonName', lessonName); // 对应 MyNote.lessonName
    formData.append('file', file);           // 上传文件，后端会生成文件路径存储到MyNote.file

    const headers = {};
    if (options.token) {
      headers['Authorization'] = `Bearer ${options.token}`;
    }

    const response = await fetch(`${baseUrl}/upload/note`, {
      method: 'POST',
      body: formData,
      headers: headers,
      credentials: options.includeCredentials ? 'include' : 'same-origin'
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`上传笔记失败: ${response.status} ${response.statusText} - ${errorText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('上传笔记时发生错误:', error);
    throw error;
  }
}

/**
 * 获取课程的所有笔记
 * @param {string} courseName - 课程名称
 * @param {string} baseUrl - API基础URL
 * @param {Object} options - 可选配置
 * @returns {Promise<Array>} 笔记列表
 */
export async function getNotesByCourse(courseName, baseUrl = 'https://example.com', options = {}) {
  try {
    const headers = {
      'Accept': 'application/json'
    };

    if (options.token) {
      headers['Authorization'] = `Bearer ${options.token}`;
    }

    const response = await fetch(`${baseUrl}/courses/${encodeURIComponent(courseName)}/notes`, {
      method: 'GET',
      headers: headers,
      credentials: options.includeCredentials ? 'include' : 'same-origin'
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`获取课程笔记失败: ${response.status} ${response.statusText} - ${errorText}`);
    }

    const notes = await response.json();
    return notes;
  } catch (error) {
    console.error('获取课程笔记时发生错误:', error);
    throw error;
  }
}