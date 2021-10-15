from rest_framework.routers import SimpleRouter

from leaderboard.apis.rest_api import CompetitionViewSet, SubmissionViewSet, UserViewSet

router = SimpleRouter()

router.register('submissions', SubmissionViewSet)
router.register('users', UserViewSet)
router.register('competitions', CompetitionViewSet)


app_name = 'api'
urlpatterns = router.urls
