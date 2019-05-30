import * as vcx from 'node-vcx-wrapper'
import uuid = require('uuid')
import { IProofMessage } from '..'
import { Agency, IAgencyConfig } from '../../../'
import { generateProblemReport } from '../../../../../services/agency/utils/problem-reports'

export class UnfulfilledProof {

    private message: IProofMessage
    private myConnection: vcx.Connection
    private proof: vcx.Proof
    private config: IAgencyConfig
    private state: vcx.StateType

    constructor(message: IProofMessage, connection: vcx.Connection, config: IAgencyConfig) {
        this.message = message
        this.myConnection = connection
        this.config = config
    }

    public async proofRequest() {
        try {
            this.proof = await vcx.Proof.create({
                sourceId: uuid(),
                attrs: this.message.proof.proofAttrs,
                name: this.message.proof.name,
                revocationInterval: {},
            })
            await this.proof.requestProof(this.myConnection)
            Agency.postResponse(this.generateStatusReport(
                0, 'Successfully sent proof request', this.message), this.config)
            this.state = await this.proof.getState()
            this.updateProofState()
        } catch (e) {
            Agency.postResponse(generateProblemReport(
                'vs.service/proof/0.1/problem-report',
                'failed to send proof request',
                this.message['@id']), this.config)
        }
    }

    private async updateProofState() {
        setTimeout(async () => {
            await this.proof.updateState()
            const { proof, proofState } = await this.proof.getProof(this.myConnection)
            this.state = await this.proof.getState()
            if (this.state === vcx.StateType.OfferSent) {
                if (proofState === vcx.ProofState.Verified) {
                    Agency.postResponse(this.generateStatusReport(
                        1, 'Proof recieved and validated', this.message, proof), this.config)
                } else {
                    Agency.postResponse(generateProblemReport(
                        'vs.service/proof/0.1/problem-report',
                        'proof recieved but was invalid!',
                        this.message['@id'],
                    ), this.config)
                }
            } else {
                this.updateProofState()
            }}, 2000)
    }

    private generateStatusReport(status: number, statusMessage: string, message: IProofMessage, content?: any) {
        let msg = {
            '@type': 'vs.service/proof/0.1/status',
            '@id': uuid(),
            '~thread': {
                pthid: message['@id'],
                seqnum: 0,
            },
            status,
            'message': statusMessage,
        }
        if (content) { msg = Object.assign({}, { ...msg, content}) }
        return msg
    }
}
