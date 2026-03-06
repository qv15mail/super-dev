## ADDED Requirements

### Requirement: business-core-flow

SHALL 系统应完整支持以下业务目标：update --method pip。请结合以下上下文实现：本地知识参考: WORKFLOW_GUIDE_EN - Host hard gate is enabled by default. If no `ready` host is available, pipeline execution is blocked until onboarding is complete.；本地知识参考: 2026-03-04-web-dashboard-host-threshold-design - 4. Backend updates `super-dev.yaml` and runs pipeline with these values.；本地知识参考: tech_practices - export async function updateProfile(formData: FormData) {；外部最佳实践: Interaction design patterns | Qubstudio - Learn about the benefits of using interaction design patterns in UI . These potent tools may improve user experiences and optimize the design process.；外部最佳实践: Top 11 User Onboarding Best Practices | Chameleon - Follow these user onboarding best practices to increase retention and keep users engaged.；外部最佳实践: User Onboarding Best Practices : +10 Do's and Dont's - See how user onboarding can help you achive business goals and aquire loyal customers. Discover a set of UX onboarding best practices .

#### Scenario 1: 按业务路径完成主要操作
- GIVEN 用户进入系统首页
- WHEN 按业务路径完成主要操作
- THEN 系统成功返回结果并展示下一步引导
