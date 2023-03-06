pipeline {
    agent {
        label 'uli42'
    }
    stages {
        stage('Skip check') {
            steps {
                script {
                    def skipPipeline = false
                    if (skipPipeline) {
                        error 'Skipping pipeline execution as specified'
                    }
                }
            }
        }
        stage('Update') {
            steps {
                bat(script: "C:\\Tools\\jenkins-agent\\jenkins-scripts\\vrx619_update_branch.bat %branch%")
            }
        }
        stage('Build') {
            steps {
                bat(script: "C:\\Tools\\jenkins-agent\\jenkins-scripts\\vrx619_build.bat")
            }
        }
        stage('FW Download') {
            agent {
                label 'uli46'
            }
            steps {
                bat(script: "C:\\Tools\\jenkins-agent\\jenkins-scripts\\FwDownload_Tftp.bat")
            }
        }
        stage('Nightly Tests') {
            agent {
                label 'uli46'
            }
            steps {
                bat(script: "C:\\Tools\\jenkins-agent\\jenkins-scripts\\Nightly_tests.bat")
            }
        }
        stage('Copy to ALAB') {
            agent {
                label 'uli46'
            }
            steps {
                bat(script: "C:\\Tools\\jenkins-agent\\jenkins-scripts\\copy_to_alab.bat")
            }
        }
    }
    post {
        failure {
            mail to: 'staider@maxlinear.com, sgreef@maxlinear.com, mbelghanou@maxlinear.com',
                subject: "FAILURE: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: "Unfortunately, the VRX619 pipeline has failed. Please check the logs for more information."
        }
    }
}
