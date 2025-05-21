// 平台判断工具
export const isH5 = process.env.UNI_PLATFORM === 'h5'
export const isWeapp = process.env.UNI_PLATFORM === 'mp-weixin'
export const isApp = process.env.UNI_PLATFORM === 'app-plus'

// 条件编译示例
export function platformSpecificAction() {
  // #ifdef H5
  console.log('H5平台特定代码')
  return 'h5'
  // #endif
  
  // #ifdef MP-WEIXIN
  console.log('微信小程序特定代码')
  return 'mp-weixin'
  // #endif
  
  // #ifdef APP-PLUS
  console.log('App特定代码')
  return 'app-plus'
  // #endif
}