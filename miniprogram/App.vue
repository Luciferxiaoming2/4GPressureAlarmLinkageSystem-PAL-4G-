<script>
	export default {
		onLaunch: function() {
			console.log('PAL_4G miniprogram launch')
		},
		onShow: function() {
			console.log('PAL_4G miniprogram show')
		},
		onHide: function() {
			console.log('PAL_4G miniprogram hide')
		}
	}
</script>

<style lang="scss">
	/*每个页面公共css */
page {
  min-height: 100%;
  background:
    radial-gradient(circle at top left, rgba(31, 111, 235, 0.16), transparent 42%),
    linear-gradient(180deg, #f3f7ff 0%, #f7fbff 48%, #eef3fb 100%);
  color: #17324d;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

view,
text,
button,
input,
picker {
  box-sizing: border-box;
}

.app-page {
  min-height: 100vh;
  padding: 28rpx 24rpx 44rpx;
}

.app-page--docked {
  padding-bottom: calc(184rpx + env(safe-area-inset-bottom));
}

.hero-panel,
.panel-card {
  border: 1rpx solid rgba(26, 70, 126, 0.08);
  border-radius: 28rpx;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 16rpx 40rpx rgba(38, 76, 131, 0.08);
  backdrop-filter: blur(16rpx);
}

.hero-panel {
  padding: 30rpx;
  background:
    linear-gradient(135deg, rgba(14, 92, 193, 0.96) 0%, rgba(32, 138, 214, 0.92) 100%);
  color: #fff;
}

.panel-card {
  padding: 28rpx;
}

.app-page > .hero-panel,
.app-page > .panel-card {
  margin-bottom: 22rpx;
}

.app-page > .hero-panel:last-child,
.app-page > .panel-card:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #17324d;
}

.section-subtitle {
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #68809d;
}

.text-muted {
  color: #6d84a1;
}

.text-strong {
  color: #17324d;
  font-weight: 600;
}

.status-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 108rpx;
  height: 46rpx;
  padding: 0 18rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 600;
}

.status-online {
  background: rgba(28, 184, 111, 0.14);
  color: #0b8e52;
}

.status-offline {
  background: rgba(130, 148, 166, 0.16);
  color: #6d84a1;
}

.status-alarm {
  background: rgba(231, 77, 60, 0.14);
  color: #cf3c2b;
}

.status-pending {
  background: rgba(255, 164, 38, 0.14);
  color: #bf7812;
}

.status-info {
  background: rgba(31, 111, 235, 0.14);
  color: #1f6feb;
}

.primary-button,
.secondary-button,
.danger-button {
  width: 100%;
  border-radius: 22rpx;
  font-size: 28rpx;
  font-weight: 600;
  min-height: 88rpx;
  line-height: 1.3;
  padding: 22rpx 24rpx;
  white-space: normal;
}

.primary-button {
  color: #fff;
  background: linear-gradient(135deg, #165dff 0%, #0f8bff 100%);
}

.secondary-button {
  color: #165dff;
  background: rgba(22, 93, 255, 0.08);
}

.danger-button {
  color: #fff;
  background: linear-gradient(135deg, #e04a36 0%, #f06d3b 100%);
}

.form-field {
  margin-bottom: 24rpx;
}

.form-label {
  margin-bottom: 12rpx;
  font-size: 24rpx;
  font-weight: 600;
  color: #35506d;
}

.form-input,
.form-textarea {
  width: 100%;
  border: 1rpx solid rgba(33, 84, 141, 0.12);
  border-radius: 20rpx;
  background: rgba(255, 255, 255, 0.9);
  min-height: 92rpx;
  padding: 24rpx 22rpx;
  font-size: 28rpx;
  color: #17324d;
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: #94a7bd;
}

.link-button {
  display: inline-flex;
  align-items: center;
  color: #165dff;
  font-size: 24rpx;
  font-weight: 600;
}

.stack-actions {
  display: grid;
  gap: 16rpx;
}

.stack-list {
  display: grid;
  gap: 18rpx;
}

.surface-link {
  color: #165dff;
  font-size: 24rpx;
  font-weight: 600;
}
</style>
