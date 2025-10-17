<script setup>
const props = defineProps({ visible: Boolean });
</script>

<template>
    <div v-show="visible" class="global-mask">
        <div class="container">
            <div class="form-card">
                <h1>新建课程</h1>
                <form id="courseForm">
                    <div class="form-group">
                        <label for="courseName">课程名称</label>
                        <input type="text" id="courseName" placeholder="请输入课程名称" required>
                    </div>

                    <div class="form-group">
                        <div class="tags-section">
                            <div class="tags-column">
                                <div class="section-title">添加课程标签</div>
                                <div class="tag-input-container">
                                    <input type="text" id="courseTags" placeholder="输入标签后按回车添加">
                                    <div class="tag-hint">输入标签后按回车键添加</div>
                                </div>
                                <div class="tags-container" id="tagsContainer">
                                    <div class="empty-state">暂无标签，请添加或从右侧选择</div>
                                </div>
                            </div>

                            <div class="tags-column">
                                <div class="section-title">从已有标签选择</div>
                                <div class="available-tags" id="availableTags">
                                    <!-- 已有标签将通过JavaScript动态生成 -->
                                </div>
                            </div>
                        </div>
                    </div>

                    <button type="submit" class="btn-submit">创建课程</button>
                </form>
            </div>
        </div>
    </div>

</template>

<style scoped>
.global-mask {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.6);
    /* 品牌主色调遮罩 */
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}

.container {
    width: 100%;
    max-width: 600px;
}

.form-card {
    background: white;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    padding: 40px;
    transition: transform 0.3s ease;
}

.form-card:hover {
    transform: translateY(-5px);
}

h1 {
    color: #2c3e50;
    margin-bottom: 30px;
    text-align: center;
    font-weight: 600;
    font-size: 28px;
}

.form-group {
    margin-bottom: 25px;
}

label {
    display: block;
    margin-bottom: 8px;
    color: #34495e;
    font-weight: 500;
    font-size: 16px;
}

input[type="text"] {
    width: 100%;
    padding: 14px 16px;
    border: 2px solid #e1e8ed;
    border-radius: 10px;
    font-size: 16px;
    transition: all 0.3s;
    background-color: #f8f9fa;
}

input[type="text"]:focus {
    outline: none;
    border-color: #3498db;
    background-color: white;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
}

.tags-section {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.tags-column {
    flex: 1;
    min-width: 250px;
}

.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 10px;
    min-height: 50px;
    padding: 15px;
    border-radius: 10px;
    background-color: #f8f9fa;
    border: 1px dashed #e1e8ed;
}

.available-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 10px;
    padding: 15px;
    border-radius: 10px;
    background-color: #f8f9fa;
    border: 1px solid #e1e8ed;
    max-height: 150px;
    overflow-y: auto;
}

.tag {
    background: #3498db;
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    display: flex;
    align-items: center;
    font-size: 14px;
    animation: fadeIn 0.3s ease;
    cursor: default;
}

.available-tag {
    background: #95a5a6;
    cursor: pointer;
    transition: all 0.2s;
}

.available-tag:hover {
    background: #7f8c8d;
    transform: scale(1.05);
}

.tag-remove {
    margin-left: 8px;
    cursor: pointer;
    font-weight: bold;
    background: none;
    border: none;
    color: white;
    font-size: 16px;
}

.tag-input-container {
    position: relative;
}

.tag-hint {
    color: #7f8c8d;
    font-size: 13px;
    margin-top: 5px;
}

.section-title {
    font-size: 18px;
    color: #2c3e50;
    margin-bottom: 15px;
    padding-bottom: 8px;
    border-bottom: 2px solid #3498db;
}

.btn-submit {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
    border: none;
    padding: 16px 24px;
    border-radius: 10px;
    font-size: 18px;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    margin-top: 10px;
}

.btn-submit:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
}

.btn-submit:active {
    transform: translateY(0);
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.8);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }
}

.success-message {
    background: #2ecc71;
    color: white;
    padding: 16px;
    border-radius: 10px;
    text-align: center;
    margin-top: 20px;
    display: none;
    animation: fadeIn 0.5s ease;
}

.empty-state {
    color: #7f8c8d;
    font-style: italic;
    text-align: center;
    padding: 10px;
}

@media (max-width: 600px) {
    .tags-section {
        flex-direction: column;
    }

    .form-card {
        padding: 25px;
    }
}
</style>