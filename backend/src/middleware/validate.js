/**
 * 开发：Excellent（11964948@qq.com）
 * 功能：请求体验证中间件
 * 作用：对 POST/PUT/PATCH 请求进行基础输入验证
 * 创建时间：2026-03-20
 * 最后修改：2026-03-20
 */

/**
 * 验证请求体不为空且为合法对象
 *
 * @param {string[]} requiredFields - 必填字段列表
 * @returns {Function} Express 中间件
 */
function validateBody(requiredFields = []) {
  return (req, res, next) => {
    if (!req.body || typeof req.body !== 'object' || Array.isArray(req.body)) {
      return res.status(400).json({
        error: {
          code: 'VALIDATION_ERROR',
          message: '请求体必须为 JSON 对象',
        },
      });
    }

    const missing = requiredFields.filter(field => {
      const value = req.body[field];
      return value === undefined || value === null || value === '';
    });

    if (missing.length > 0) {
      return res.status(422).json({
        error: {
          code: 'VALIDATION_ERROR',
          message: '缺少必填字段',
          details: missing.map(field => ({ field, message: `${field} 为必填字段` })),
        },
      });
    }

    next();
  };
}

module.exports = { validateBody };
